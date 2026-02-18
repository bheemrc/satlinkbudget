"""Pydantic mission configuration model."""

from __future__ import annotations

from pydantic import BaseModel, Field


class OrbitConfig(BaseModel):
    altitude_km: float
    inclination_deg: float
    raan_deg: float = 0.0
    j2: bool = True


class TransmitterConfig(BaseModel):
    transceiver: str = ""
    power_dbm: float = 33.0
    antenna: str = ""
    antenna_gain_dbi: float = 0.0
    feed_loss_db: float = 0.0
    pointing_error_deg: float = 0.0


class ReceiverConfig(BaseModel):
    ground_station: str = ""
    antenna_gain_dbi: float = 0.0
    system_noise_temp_k: float = 150.0
    lna_noise_figure_db: float = 1.0
    feed_loss_db: float = 0.0
    pointing_error_deg: float = 0.0


class ModemConfigYaml(BaseModel):
    modulation: str = "BPSK"
    coding: str = "uncoded"
    implementation_loss_db: float = 1.0
    data_rate_bps: float = 9600.0


class AtmosphereConfig(BaseModel):
    rain_rate_001_mm_h: float = 0.0
    latitude_deg: float = 45.0
    liquid_water_content_kg_m2: float = 0.0
    include_scintillation: bool = False


class SimulationConfig(BaseModel):
    duration_orbits: float = 24.0
    dt_s: float = 1.0
    contact_dt_s: float = 10.0


class LinkMissionConfig(BaseModel):
    """Top-level mission configuration."""

    name: str
    frequency_hz: float
    orbit: OrbitConfig
    transmitter: TransmitterConfig = Field(default_factory=TransmitterConfig)
    receiver: ReceiverConfig = Field(default_factory=ReceiverConfig)
    modem: ModemConfigYaml = Field(default_factory=ModemConfigYaml)
    atmosphere: AtmosphereConfig = Field(default_factory=AtmosphereConfig)
    simulation: SimulationConfig = Field(default_factory=SimulationConfig)
