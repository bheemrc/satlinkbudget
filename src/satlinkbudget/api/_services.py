"""Service layer: connects API schemas to satlinkbudget internals."""

from __future__ import annotations

import asyncio
import uuid
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import yaml

from satlinkbudget.api._schemas import (
    ComponentDetailResponse,
    ComponentInfo,
    ComponentListResponse,
    LinkBudgetRequest,
    LinkBudgetResponse,
    LinkBudgetSummary,
    MaxDataRateRequest,
    MaxDataRateResponse,
    PassSimulationRequest,
    PassSimulationResponse,
    PassSummary,
    PlotFormat,
    PresetInfo,
    PresetListResponse,
    PresetSimulationRequest,
    RequiredPowerRequest,
    RequiredPowerResponse,
    SimulationSummary,
)
from satlinkbudget.api._serializers import (
    serialize_plot_data_volume,
    serialize_plot_doppler,
    serialize_plot_elevation,
    serialize_plot_margin,
    serialize_plot_waterfall,
)
from satlinkbudget.api._errors import ConfigurationError, ComponentNotFoundError
from satlinkbudget.budget._transmitter import TransmitterChain
from satlinkbudget.budget._receiver import ReceiverChain
from satlinkbudget.budget._link import (
    compute_link_budget,
    compute_max_data_rate,
    compute_required_power_dbw,
)
from satlinkbudget.modem._modulation import BPSK, QPSK, PSK8, QAM16
from satlinkbudget.modem._coding import (
    UNCODED,
    CONV_R12_K7,
    TURBO_R12,
    LDPC_R12,
    LDPC_R34,
    LDPC_R78,
)
from satlinkbudget.modem._performance import ModemConfig
from satlinkbudget.mission._config import LinkMissionConfig
from satlinkbudget.mission._builder import build_pass_simulation
from satlinkbudget.simulation._report import generate_report
from satlinkbudget.data._registry import registry


_executor = ThreadPoolExecutor(max_workers=4)

_MOD_MAP = {"BPSK": BPSK, "QPSK": QPSK, "8PSK": PSK8, "16QAM": QAM16}
_CODE_MAP = {
    "uncoded": UNCODED,
    "convolutional_r12": CONV_R12_K7,
    "turbo_r12": TURBO_R12,
    "ldpc_r12": LDPC_R12,
    "ldpc_r34": LDPC_R34,
    "ldpc_r78": LDPC_R78,
}


def _build_modem(modulation: str, coding: str, impl_loss: float) -> ModemConfig:
    """Build ModemConfig from string identifiers."""
    mod = _MOD_MAP.get(modulation, BPSK)
    code = _CODE_MAP.get(coding, UNCODED)
    return ModemConfig(mod, code, impl_loss)


# --- Link budget ---


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

    modem = _build_modem(request.modulation, request.coding, request.implementation_loss_db)
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
        misc_loss_db=request.misc_loss_db,
    )

    summary = LinkBudgetSummary(
        eirp_dbw=result.eirp_dbw,
        figure_of_merit_db_per_k=result.figure_of_merit_db_per_k,
        free_space_path_loss_db=result.free_space_path_loss_db,
        atmospheric_loss_db=result.atmospheric_loss_db,
        polarization_loss_db=result.polarization_loss_db,
        misc_loss_db=result.misc_loss_db,
        c_over_n0_db_hz=result.c_over_n0_db_hz,
        eb_n0_db=result.eb_n0_db,
        required_eb_n0_db=result.required_eb_n0_db,
        margin_db=result.margin_db,
        link_closes=result.link_closes,
    )

    waterfall = serialize_plot_waterfall(result, request.plot_format)

    return LinkBudgetResponse(
        simulation_id=str(uuid.uuid4()),
        summary=summary,
        text_report=result.to_text(),
        waterfall_plot=waterfall,
    )


async def run_link_budget_async(request: LinkBudgetRequest) -> LinkBudgetResponse:
    """Async wrapper for run_link_budget."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, run_link_budget, request)


# --- Max data rate ---


def run_max_data_rate(request: MaxDataRateRequest) -> MaxDataRateResponse:
    """Compute maximum data rate that closes the link."""
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

    modem = _build_modem(request.modulation, request.coding, request.implementation_loss_db)
    required = modem.required_eb_n0_db()

    rate = compute_max_data_rate(
        transmitter=tx,
        receiver=rx,
        frequency_hz=request.frequency_hz,
        distance_m=request.distance_m,
        required_eb_n0_db=required,
        target_margin_db=request.target_margin_db,
        atmospheric_loss_db=request.atmospheric_loss_db,
        polarization_loss_db=request.polarization_loss_db,
        misc_loss_db=request.misc_loss_db,
    )

    return MaxDataRateResponse(
        simulation_id=str(uuid.uuid4()),
        max_data_rate_bps=rate,
        max_data_rate_kbps=rate / 1e3,
        link_closes=rate > 0.0,
    )


# --- Required power ---


def run_required_power(request: RequiredPowerRequest) -> RequiredPowerResponse:
    """Compute minimum TX power to close the link."""
    rx = ReceiverChain(
        antenna_gain_dbi=request.rx_antenna_gain_dbi,
        system_noise_temp_k=request.rx_system_noise_temp_k,
        feed_loss_db=request.rx_feed_loss_db,
    )

    modem = _build_modem(request.modulation, request.coding, request.implementation_loss_db)
    required = modem.required_eb_n0_db()

    power_dbw = compute_required_power_dbw(
        receiver=rx,
        frequency_hz=request.frequency_hz,
        distance_m=request.distance_m,
        data_rate_bps=request.data_rate_bps,
        required_eb_n0_db=required,
        target_margin_db=request.target_margin_db,
        tx_antenna_gain_dbi=request.tx_antenna_gain_dbi,
        tx_feed_loss_db=request.tx_feed_loss_db,
        atmospheric_loss_db=request.atmospheric_loss_db,
        polarization_loss_db=request.polarization_loss_db,
        misc_loss_db=request.misc_loss_db,
    )

    power_dbm = power_dbw + 30.0
    power_w = 10.0 ** (power_dbw / 10.0)

    return RequiredPowerResponse(
        simulation_id=str(uuid.uuid4()),
        required_power_dbw=power_dbw,
        required_power_dbm=power_dbm,
        required_power_w=power_w,
    )


# --- Pass simulation ---


def _load_mission_config(request: PassSimulationRequest) -> LinkMissionConfig:
    """Load mission config from request."""
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

    return LinkMissionConfig(**data)


def run_pass_simulation(request: PassSimulationRequest) -> PassSimulationResponse:
    """Run a pass simulation from request parameters."""
    config = _load_mission_config(request)

    sim = build_pass_simulation(config)
    results = sim.run(
        duration_orbits=request.duration_orbits,
        dt_s=request.dt_s,
        contact_dt_s=config.simulation.contact_dt_s,
    )

    report = generate_report(results)

    # Per-pass summaries
    pass_summaries = [
        PassSummary(
            pass_number=p.pass_number,
            start_time_s=p.start_time_s,
            end_time_s=p.end_time_s,
            duration_s=p.duration_s,
            max_elevation_deg=p.max_elevation_deg,
            min_margin_db=p.min_margin_db,
            max_margin_db=p.max_margin_db,
            data_volume_bits=p.data_volume_bits,
            data_volume_kbytes=p.data_volume_kbytes,
        )
        for p in results.passes
    ]

    summary = SimulationSummary(
        num_passes=results.num_passes,
        total_contact_time_s=results.total_contact_time_s,
        passes_per_day=results.passes_per_day,
        total_data_volume_bits=results.total_data_volume_bits,
        total_data_volume_mbytes=results.total_data_volume_mbytes,
        avg_pass_duration_s=results.avg_pass_duration_s,
        frequency_hz=results.frequency_hz,
        data_rate_bps=results.data_rate_bps,
    )

    # Plots (for the first pass if available)
    plots = []
    fmt = request.plot_format
    if results.num_passes > 0:
        plots.append(serialize_plot_elevation(results, fmt, pass_idx=0))
        plots.append(serialize_plot_margin(results, fmt, pass_idx=0))
        plots.append(serialize_plot_doppler(results, fmt, pass_idx=0))
    plots.append(serialize_plot_data_volume(results, fmt))

    return PassSimulationResponse(
        simulation_id=str(uuid.uuid4()),
        summary=summary,
        passes=pass_summaries,
        text_report=report,
        plots=plots,
    )


async def run_pass_simulation_async(
    request: PassSimulationRequest,
) -> PassSimulationResponse:
    """Async wrapper for run_pass_simulation (CPU-bound, runs in thread pool)."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, run_pass_simulation, request)


# --- Preset simulation ---


def run_preset(request: PresetSimulationRequest) -> PassSimulationResponse:
    """Run a bundled preset mission with optional overrides."""
    available = registry.list_missions()
    if request.preset_name not in available:
        raise ConfigurationError(
            f"Preset '{request.preset_name}' not found. "
            f"Available: {', '.join(available)}"
        )

    from pathlib import Path
    missions_dir = Path(__file__).parent.parent / "data" / "missions"
    mission_path = missions_dir / f"{request.preset_name}.yaml"
    with open(mission_path) as f:
        data = yaml.safe_load(f)

    # Apply overrides (dot-notation: "orbit.altitude_km", "modem.data_rate_bps")
    for key, value in request.overrides.items():
        parts = key.split(".")
        target = data
        for part in parts[:-1]:
            if part not in target:
                target[part] = {}
            target = target[part]
        target[parts[-1]] = value

    config = LinkMissionConfig(**data)
    sim = build_pass_simulation(config)
    results = sim.run(
        duration_orbits=request.duration_orbits,
        dt_s=request.dt_s,
        contact_dt_s=config.simulation.contact_dt_s,
    )

    report = generate_report(results)

    pass_summaries = [
        PassSummary(
            pass_number=p.pass_number,
            start_time_s=p.start_time_s,
            end_time_s=p.end_time_s,
            duration_s=p.duration_s,
            max_elevation_deg=p.max_elevation_deg,
            min_margin_db=p.min_margin_db,
            max_margin_db=p.max_margin_db,
            data_volume_bits=p.data_volume_bits,
            data_volume_kbytes=p.data_volume_kbytes,
        )
        for p in results.passes
    ]

    summary = SimulationSummary(
        num_passes=results.num_passes,
        total_contact_time_s=results.total_contact_time_s,
        passes_per_day=results.passes_per_day,
        total_data_volume_bits=results.total_data_volume_bits,
        total_data_volume_mbytes=results.total_data_volume_mbytes,
        avg_pass_duration_s=results.avg_pass_duration_s,
        frequency_hz=results.frequency_hz,
        data_rate_bps=results.data_rate_bps,
    )

    fmt = request.plot_format
    plots = []
    if results.num_passes > 0:
        plots.append(serialize_plot_elevation(results, fmt, pass_idx=0))
        plots.append(serialize_plot_margin(results, fmt, pass_idx=0))
        plots.append(serialize_plot_doppler(results, fmt, pass_idx=0))
    plots.append(serialize_plot_data_volume(results, fmt))

    return PassSimulationResponse(
        simulation_id=str(uuid.uuid4()),
        summary=summary,
        passes=pass_summaries,
        text_report=report,
        plots=plots,
    )


async def run_preset_async(
    request: PresetSimulationRequest,
) -> PassSimulationResponse:
    """Async wrapper for run_preset."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, run_preset, request)


# --- Component catalog ---


def list_components(category: str) -> ComponentListResponse:
    """List all components in a category with highlights."""
    if category == "transceivers":
        names = registry.list_transceivers()
        components = []
        for name in names:
            data = registry.get_transceiver(name)
            components.append(
                ComponentInfo(
                    name=name,
                    category=category,
                    highlights={
                        "tx_power_dbm": data.tx_power_dbm,
                        "frequency_hz": data.frequency_hz,
                        "data_rate_bps": data.data_rate_bps,
                    },
                )
            )
    elif category == "antennas":
        names = registry.list_antennas()
        components = []
        for name in names:
            data = registry.get_antenna(name)
            components.append(
                ComponentInfo(
                    name=name,
                    category=category,
                    highlights={
                        "gain_dbi": data.gain_dbi,
                        "beamwidth_deg": data.beamwidth_deg,
                    },
                )
            )
    elif category == "groundstations":
        names = registry.list_groundstations()
        components = []
        for name in names:
            data = registry.get_groundstation(name)
            components.append(
                ComponentInfo(
                    name=name,
                    category=category,
                    highlights={
                        "latitude_deg": data.latitude_deg,
                        "longitude_deg": data.longitude_deg,
                        "antenna_gain_dbi": data.antenna_gain_dbi,
                    },
                )
            )
    elif category == "bands":
        names = registry.list_bands()
        components = []
        for name in names:
            data = registry.get_band(name)
            components.append(
                ComponentInfo(
                    name=name,
                    category=category,
                    highlights={
                        "designation": data.designation,
                        "downlink_min_hz": data.downlink_min_hz,
                        "downlink_max_hz": data.downlink_max_hz,
                    },
                )
            )
    else:
        raise ComponentNotFoundError(f"Unknown category: {category}")

    return ComponentListResponse(category=category, components=components)


def get_component(category: str, name: str) -> ComponentDetailResponse:
    """Get full details for a single component."""
    try:
        if category == "transceivers":
            data = registry.get_transceiver(name)
        elif category == "antennas":
            data = registry.get_antenna(name)
        elif category == "groundstations":
            data = registry.get_groundstation(name)
        elif category == "bands":
            data = registry.get_band(name)
        else:
            raise ComponentNotFoundError(f"Unknown category: {category}")
    except KeyError as e:
        raise ComponentNotFoundError(str(e)) from e

    return ComponentDetailResponse(
        name=name,
        category=category,
        data=data.model_dump(),
    )


def get_presets() -> PresetListResponse:
    """List available mission presets."""
    names = registry.list_missions()
    presets = []
    for name in names:
        try:
            from satlinkbudget.mission._builder import load_mission
            config = load_mission(
                str(
                    __import__("pathlib").Path(__file__).parent.parent
                    / "data"
                    / "missions"
                    / f"{name}.yaml"
                )
            )
            presets.append(PresetInfo(name=name, description=config.name))
        except Exception:
            presets.append(PresetInfo(name=name))

    return PresetListResponse(presets=presets)
