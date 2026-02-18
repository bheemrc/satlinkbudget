"""Load mission config and build simulation."""

from __future__ import annotations

from pathlib import Path

import yaml

from satlinkbudget.mission._config import LinkMissionConfig
from satlinkbudget.simulation._engine import PassSimulation
from satlinkbudget.orbit._propagator import Orbit
from satlinkbudget.orbit._groundstation import GroundStation
from satlinkbudget.budget._transmitter import TransmitterChain
from satlinkbudget.budget._receiver import ReceiverChain
from satlinkbudget.modem._performance import ModemConfig
from satlinkbudget.modem._modulation import BPSK, QPSK, PSK8, QAM16, ModulationScheme
from satlinkbudget.modem._coding import (
    UNCODED,
    CONV_R12_K7,
    TURBO_R12,
    LDPC_R12,
    LDPC_R34,
    LDPC_R78,
    CodingScheme,
)
from satlinkbudget.data._registry import registry
from satlinkbudget.antenna._pointing import pointing_loss_db


_MODULATION_MAP: dict[str, ModulationScheme] = {
    "BPSK": BPSK,
    "QPSK": QPSK,
    "8PSK": PSK8,
    "16QAM": QAM16,
}

_CODING_MAP: dict[str, CodingScheme] = {
    "uncoded": UNCODED,
    "convolutional_r12": CONV_R12_K7,
    "turbo_r12": TURBO_R12,
    "ldpc_r12": LDPC_R12,
    "ldpc_r34": LDPC_R34,
    "ldpc_r78": LDPC_R78,
}


def load_mission(path: str | Path) -> LinkMissionConfig:
    """Load mission configuration from YAML file."""
    with open(path) as f:
        data = yaml.safe_load(f)
    return LinkMissionConfig(**data)


def build_pass_simulation(config: LinkMissionConfig) -> PassSimulation:
    """Build PassSimulation from mission configuration."""
    # Orbit
    orbit = Orbit.circular(
        altitude_km=config.orbit.altitude_km,
        inclination_deg=config.orbit.inclination_deg,
        raan_deg=config.orbit.raan_deg,
        j2=config.orbit.j2,
    )

    # Ground station
    if config.receiver.ground_station:
        gs_data = registry.get_groundstation(config.receiver.ground_station)
        gs = GroundStation(
            name=gs_data.name,
            latitude_deg=gs_data.latitude_deg,
            longitude_deg=gs_data.longitude_deg,
            altitude_m=gs_data.altitude_m,
            min_elevation_deg=gs_data.min_elevation_deg,
        )
        rx_gain = gs_data.antenna_gain_dbi or config.receiver.antenna_gain_dbi
        rx_noise = gs_data.system_noise_temp_k or config.receiver.system_noise_temp_k
    else:
        gs = GroundStation(
            name="Custom",
            latitude_deg=config.atmosphere.latitude_deg,
            longitude_deg=0.0,
        )
        rx_gain = config.receiver.antenna_gain_dbi
        rx_noise = config.receiver.system_noise_temp_k

    # Transmitter
    if config.transmitter.transceiver:
        tx_data = registry.get_transceiver(config.transmitter.transceiver)
        tx_power_dbm = tx_data.tx_power_dbm
    else:
        tx_power_dbm = config.transmitter.power_dbm

    if config.transmitter.antenna:
        ant_data = registry.get_antenna(config.transmitter.antenna)
        tx_gain = ant_data.gain_dbi
        tx_bw = ant_data.beamwidth_deg
    else:
        tx_gain = config.transmitter.antenna_gain_dbi
        tx_bw = 90.0  # default wide beamwidth

    tx_pointing = 0.0
    if config.transmitter.pointing_error_deg > 0 and tx_bw > 0:
        tx_pointing = pointing_loss_db(config.transmitter.pointing_error_deg, tx_bw)

    transmitter = TransmitterChain.from_power_dbm(
        power_dbm=tx_power_dbm,
        antenna_gain_dbi=tx_gain,
        feed_loss_db=config.transmitter.feed_loss_db,
        pointing_loss_db=tx_pointing,
    )

    # Receiver
    rx_pointing = 0.0
    receiver = ReceiverChain(
        antenna_gain_dbi=rx_gain,
        system_noise_temp_k=rx_noise,
        feed_loss_db=config.receiver.feed_loss_db,
        pointing_loss_db=rx_pointing,
    )

    # Modem
    modulation = _MODULATION_MAP.get(config.modem.modulation, BPSK)
    coding = _CODING_MAP.get(config.modem.coding, UNCODED)
    modem = ModemConfig(
        modulation=modulation,
        coding=coding,
        implementation_loss_db=config.modem.implementation_loss_db,
    )

    # Atmospheric parameters
    atm_params = {
        "rain_rate_001_mm_h": config.atmosphere.rain_rate_001_mm_h,
        "latitude_deg": config.atmosphere.latitude_deg,
        "liquid_water_content_kg_m2": config.atmosphere.liquid_water_content_kg_m2,
        "include_scintillation": config.atmosphere.include_scintillation,
    }

    return PassSimulation(
        orbit=orbit,
        ground_station=gs,
        transmitter=transmitter,
        receiver=receiver,
        modem=modem,
        frequency_hz=config.frequency_hz,
        data_rate_bps=config.modem.data_rate_bps,
        atmospheric_params=atm_params,
    )
