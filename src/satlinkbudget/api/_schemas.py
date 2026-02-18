"""Pydantic request/response models for the API layer."""

from __future__ import annotations

from pydantic import BaseModel, Field


class LinkBudgetRequest(BaseModel):
    """Request for a single link budget computation."""

    tx_power_dbm: float = Field(description="Transmitter power [dBm]")
    tx_antenna_gain_dbi: float = Field(description="Transmitter antenna gain [dBi]")
    tx_feed_loss_db: float = Field(default=0.0)
    tx_pointing_loss_db: float = Field(default=0.0)

    rx_antenna_gain_dbi: float = Field(description="Receiver antenna gain [dBi]")
    rx_system_noise_temp_k: float = Field(description="System noise temperature [K]")
    rx_feed_loss_db: float = Field(default=0.0)

    frequency_hz: float = Field(description="Carrier frequency [Hz]")
    distance_m: float = Field(description="Link distance [m]")
    data_rate_bps: float = Field(description="Data rate [bps]")

    modulation: str = Field(default="BPSK")
    coding: str = Field(default="uncoded")
    implementation_loss_db: float = Field(default=1.0)

    atmospheric_loss_db: float = Field(default=0.0)
    polarization_loss_db: float = Field(default=0.0)


class LinkBudgetResponse(BaseModel):
    """Response from link budget computation."""

    eirp_dbw: float
    figure_of_merit_db_per_k: float
    free_space_path_loss_db: float
    c_over_n0_db_hz: float
    eb_n0_db: float
    required_eb_n0_db: float
    margin_db: float
    link_closes: bool
    text_report: str = ""


class PassSimulationRequest(BaseModel):
    """Request for a pass simulation."""

    mission_yaml: str = Field(default="", description="YAML config string")
    mission_preset: str = Field(default="", description="Preset mission name")
    duration_orbits: float = Field(default=24.0)
    dt_s: float = Field(default=1.0)


class PassSimulationResponse(BaseModel):
    """Response from pass simulation."""

    num_passes: int
    total_contact_time_s: float
    passes_per_day: float
    total_data_volume_bits: float
    total_data_volume_mbytes: float
    avg_pass_duration_s: float
    text_report: str = ""
