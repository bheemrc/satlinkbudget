"""Service functions for the API layer."""

from __future__ import annotations

import yaml

from satlinkbudget.api._schemas import (
    LinkBudgetRequest,
    LinkBudgetResponse,
    PassSimulationRequest,
    PassSimulationResponse,
)
from satlinkbudget.api._errors import ConfigurationError, ComponentNotFoundError
from satlinkbudget.budget._transmitter import TransmitterChain
from satlinkbudget.budget._receiver import ReceiverChain
from satlinkbudget.budget._link import compute_link_budget
from satlinkbudget.modem._modulation import BPSK, QPSK, PSK8, QAM16
from satlinkbudget.modem._coding import UNCODED, CONV_R12_K7, TURBO_R12, LDPC_R12, LDPC_R34, LDPC_R78
from satlinkbudget.modem._performance import ModemConfig
from satlinkbudget.mission._config import LinkMissionConfig
from satlinkbudget.mission._builder import build_pass_simulation
from satlinkbudget.simulation._report import generate_report
from satlinkbudget.data._registry import registry


_MOD_MAP = {"BPSK": BPSK, "QPSK": QPSK, "8PSK": PSK8, "16QAM": QAM16}
_CODE_MAP = {
    "uncoded": UNCODED,
    "convolutional_r12": CONV_R12_K7,
    "turbo_r12": TURBO_R12,
    "ldpc_r12": LDPC_R12,
    "ldpc_r34": LDPC_R34,
    "ldpc_r78": LDPC_R78,
}


def run_link_budget(request: LinkBudgetRequest) -> LinkBudgetResponse:
    """Compute a single link budget from request parameters."""
    tx = TransmitterChain.from_power_dbm(
        request.tx_power_dbm,
        request.tx_antenna_gain_dbi,
        feed_loss_db=request.tx_feed_loss_db,
        pointing_loss_db=request.tx_pointing_loss_db,
    )
    rx = ReceiverChain(
        antenna_gain_dbi=request.rx_antenna_gain_dbi,
        system_noise_temp_k=request.rx_system_noise_temp_k,
        feed_loss_db=request.rx_feed_loss_db,
    )

    modulation = _MOD_MAP.get(request.modulation, BPSK)
    coding = _CODE_MAP.get(request.coding, UNCODED)
    modem = ModemConfig(modulation, coding, request.implementation_loss_db)
    required = modem.required_eb_n0_db()

    result = compute_link_budget(
        transmitter=tx,
        receiver=rx,
        frequency_hz=request.frequency_hz,
        distance_m=request.distance_m,
        data_rate_bps=request.data_rate_bps,
        required_eb_n0_db=required,
        atmospheric_loss_db=request.atmospheric_loss_db,
        polarization_loss_db=request.polarization_loss_db,
    )

    return LinkBudgetResponse(
        eirp_dbw=result.eirp_dbw,
        figure_of_merit_db_per_k=result.figure_of_merit_db_per_k,
        free_space_path_loss_db=result.free_space_path_loss_db,
        c_over_n0_db_hz=result.c_over_n0_db_hz,
        eb_n0_db=result.eb_n0_db,
        required_eb_n0_db=result.required_eb_n0_db,
        margin_db=result.margin_db,
        link_closes=result.link_closes,
        text_report=result.to_text(),
    )


def run_pass_simulation(request: PassSimulationRequest) -> PassSimulationResponse:
    """Run a pass simulation from request parameters."""
    if request.mission_preset:
        from pathlib import Path
        missions_dir = Path(__file__).parent.parent / "data" / "missions"
        mission_path = missions_dir / f"{request.mission_preset}.yaml"
        if not mission_path.exists():
            raise ConfigurationError(f"Mission preset '{request.mission_preset}' not found")
        with open(mission_path) as f:
            data = yaml.safe_load(f)
    elif request.mission_yaml:
        data = yaml.safe_load(request.mission_yaml)
    else:
        raise ConfigurationError("Either mission_yaml or mission_preset must be provided")

    config = LinkMissionConfig(**data)

    # Override duration if specified
    if request.duration_orbits != 24.0:
        config.simulation.duration_orbits = request.duration_orbits

    sim = build_pass_simulation(config)
    results = sim.run(
        duration_orbits=config.simulation.duration_orbits,
        dt_s=request.dt_s,
        contact_dt_s=config.simulation.contact_dt_s,
    )

    report = generate_report(results)

    return PassSimulationResponse(
        num_passes=results.num_passes,
        total_contact_time_s=results.total_contact_time_s,
        passes_per_day=results.passes_per_day,
        total_data_volume_bits=results.total_data_volume_bits,
        total_data_volume_mbytes=results.total_data_volume_mbytes,
        avg_pass_duration_s=results.avg_pass_duration_s,
        text_report=report,
    )


def list_components(category: str) -> list[str]:
    """List components in a category."""
    return registry.list_category(category)


def get_component(category: str, name: str) -> dict:
    """Get a component by category and name."""
    try:
        if category == "transceivers":
            return registry.get_transceiver(name).model_dump()
        elif category == "antennas":
            return registry.get_antenna(name).model_dump()
        elif category == "groundstations":
            return registry.get_groundstation(name).model_dump()
        elif category == "bands":
            return registry.get_band(name).model_dump()
        else:
            raise ComponentNotFoundError(f"Unknown category: {category}")
    except KeyError as e:
        raise ComponentNotFoundError(str(e)) from e


def get_presets() -> list[str]:
    """List available mission presets."""
    return registry.list_missions()
