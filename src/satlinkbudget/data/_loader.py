"""Pydantic models for YAML component datasheets."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class TransceiverData(BaseModel):
    """Satellite transceiver datasheet."""

    name: str
    manufacturer: str = ""
    frequency_hz: float = Field(description="Operating frequency [Hz]")
    tx_power_dbm: float = Field(description="Transmit power [dBm]")
    rx_sensitivity_dbm: float = Field(
        default=-120.0, description="Receiver sensitivity [dBm]"
    )
    data_rate_bps: float = Field(default=9600.0, description="Default data rate [bps]")
    modulation: str = Field(default="BPSK", description="Default modulation scheme")
    mass_kg: float = Field(default=0.0, description="Mass [kg]")
    power_consumption_w: float = Field(default=0.0, description="Power consumption [W]")

    @classmethod
    def from_yaml(cls, path: Path) -> TransceiverData:
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(**data)


class AntennaData(BaseModel):
    """Antenna datasheet."""

    name: str
    type: str = Field(description="Antenna type: parabolic, patch, helix, dipole, monopole, horn, yagi")
    gain_dbi: float = Field(default=0.0, description="Peak gain [dBi] at design freq")
    frequency_hz: float = Field(default=0.0, description="Design frequency [Hz]")
    beamwidth_deg: float = Field(default=360.0, description="3 dB beamwidth [deg]")
    diameter_m: float = Field(default=0.0, description="Diameter [m] (parabolic)")
    efficiency: float = Field(default=0.55, description="Aperture efficiency")
    num_elements: int = Field(default=1, description="Number of elements (array)")
    polarization: str = Field(default="linear_v", description="Polarization type")
    mass_kg: float = Field(default=0.0)

    @classmethod
    def from_yaml(cls, path: Path) -> AntennaData:
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(**data)


class GroundStationData(BaseModel):
    """Ground station datasheet."""

    name: str
    operator: str = ""
    latitude_deg: float = Field(description="Latitude [deg]")
    longitude_deg: float = Field(description="Longitude [deg]")
    altitude_m: float = Field(default=0.0, description="Altitude above sea level [m]")
    min_elevation_deg: float = Field(default=5.0, description="Minimum elevation [deg]")
    antenna_diameter_m: float = Field(default=0.0, description="Antenna diameter [m]")
    antenna_gain_dbi: float = Field(default=0.0, description="Antenna gain [dBi]")
    antenna_type: str = Field(default="parabolic")
    system_noise_temp_k: float = Field(default=150.0, description="System noise temperature [K]")
    lna_noise_figure_db: float = Field(default=1.0, description="LNA noise figure [dB]")
    frequency_bands: list[str] = Field(default_factory=list, description="Supported bands")
    polarization: str = Field(default="rhcp")

    @classmethod
    def from_yaml(cls, path: Path) -> GroundStationData:
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(**data)


class FrequencyBandData(BaseModel):
    """Frequency band definition."""

    name: str
    designation: str = Field(description="Band designation (e.g., UHF, S, X)")
    uplink_min_hz: float = Field(default=0.0)
    uplink_max_hz: float = Field(default=0.0)
    downlink_min_hz: float = Field(default=0.0)
    downlink_max_hz: float = Field(default=0.0)
    typical_eirp_dbw: float = Field(default=0.0)
    max_bandwidth_hz: float = Field(default=0.0)
    notes: str = Field(default="")

    @classmethod
    def from_yaml(cls, path: Path) -> FrequencyBandData:
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(**data)
