"""Pydantic request/response models for the SaaS API layer."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# --- Enums ---


class PlotFormat(str, Enum):
    STRUCTURED = "structured"
    PNG_BASE64 = "png_base64"


# --- Request schemas ---


class LinkBudgetRequest(BaseModel):
    """Request for a single link budget computation."""

    tx_power_dbm: float = Field(description="Transmitter power [dBm]")
    tx_antenna_gain_dbi: float = Field(description="Transmitter antenna gain [dBi]")
    tx_feed_loss_db: float = Field(default=0.0, ge=0.0)
    tx_pointing_loss_db: float = Field(default=0.0, ge=0.0)

    rx_antenna_gain_dbi: float = Field(description="Receiver antenna gain [dBi]")
    rx_system_noise_temp_k: float = Field(description="System noise temperature [K]", gt=0.0)
    rx_feed_loss_db: float = Field(default=0.0, ge=0.0)

    frequency_hz: float = Field(description="Carrier frequency [Hz]", gt=0.0)
    distance_m: float = Field(description="Link distance [m]", gt=0.0)
    data_rate_bps: float = Field(description="Data rate [bps]", gt=0.0)

    modulation: str = Field(default="BPSK")
    coding: str = Field(default="uncoded")
    implementation_loss_db: float = Field(default=1.0, ge=0.0)

    atmospheric_loss_db: float = Field(default=0.0, ge=0.0)
    polarization_loss_db: float = Field(default=0.0, ge=0.0)
    misc_loss_db: float = Field(default=0.0, ge=0.0)

    plot_format: PlotFormat = PlotFormat.STRUCTURED


class MaxDataRateRequest(BaseModel):
    """Request for maximum data rate computation."""

    tx_power_dbm: float = Field(description="Transmitter power [dBm]")
    tx_antenna_gain_dbi: float = Field(description="Transmitter antenna gain [dBi]")
    tx_feed_loss_db: float = Field(default=0.0, ge=0.0)
    tx_pointing_loss_db: float = Field(default=0.0, ge=0.0)

    rx_antenna_gain_dbi: float = Field(description="Receiver antenna gain [dBi]")
    rx_system_noise_temp_k: float = Field(description="System noise temperature [K]", gt=0.0)
    rx_feed_loss_db: float = Field(default=0.0, ge=0.0)

    frequency_hz: float = Field(gt=0.0)
    distance_m: float = Field(gt=0.0)

    modulation: str = Field(default="BPSK")
    coding: str = Field(default="uncoded")
    implementation_loss_db: float = Field(default=1.0, ge=0.0)
    target_margin_db: float = Field(default=3.0)

    atmospheric_loss_db: float = Field(default=0.0, ge=0.0)
    polarization_loss_db: float = Field(default=0.0, ge=0.0)
    misc_loss_db: float = Field(default=0.0, ge=0.0)


class RequiredPowerRequest(BaseModel):
    """Request for required TX power computation."""

    rx_antenna_gain_dbi: float = Field(description="Receiver antenna gain [dBi]")
    rx_system_noise_temp_k: float = Field(gt=0.0)
    rx_feed_loss_db: float = Field(default=0.0, ge=0.0)

    frequency_hz: float = Field(gt=0.0)
    distance_m: float = Field(gt=0.0)
    data_rate_bps: float = Field(gt=0.0)

    modulation: str = Field(default="BPSK")
    coding: str = Field(default="uncoded")
    implementation_loss_db: float = Field(default=1.0, ge=0.0)
    target_margin_db: float = Field(default=3.0)

    tx_antenna_gain_dbi: float = Field(default=0.0)
    tx_feed_loss_db: float = Field(default=0.0, ge=0.0)
    atmospheric_loss_db: float = Field(default=0.0, ge=0.0)
    polarization_loss_db: float = Field(default=0.0, ge=0.0)
    misc_loss_db: float = Field(default=0.0, ge=0.0)


class PassSimulationRequest(BaseModel):
    """Request for a pass simulation."""

    mission_yaml: str = Field(default="", description="YAML config string")
    mission_preset: str = Field(default="", description="Preset mission name")
    duration_orbits: float = Field(default=24.0, gt=0.0)
    dt_s: float = Field(default=1.0, gt=0.0)
    plot_format: PlotFormat = PlotFormat.STRUCTURED


class PresetSimulationRequest(BaseModel):
    """Run a bundled preset mission with optional overrides."""

    preset_name: str
    overrides: dict[str, Any] = Field(default_factory=dict)
    plot_format: PlotFormat = PlotFormat.STRUCTURED
    duration_orbits: float = Field(default=24.0, gt=0.0)
    dt_s: float = Field(default=1.0, gt=0.0)


# --- Response schemas ---


class TimeSeriesData(BaseModel):
    label: str
    unit: str
    x: list[float]
    y: list[float]


class PlotData(BaseModel):
    plot_type: str
    format: PlotFormat
    time_series: list[TimeSeriesData] | None = None
    png_base64: str | None = None


class LinkBudgetSummary(BaseModel):
    eirp_dbw: float
    figure_of_merit_db_per_k: float
    free_space_path_loss_db: float
    atmospheric_loss_db: float
    polarization_loss_db: float
    misc_loss_db: float
    c_over_n0_db_hz: float
    eb_n0_db: float
    required_eb_n0_db: float
    margin_db: float
    link_closes: bool


class LinkBudgetResponse(BaseModel):
    """Response from link budget computation."""

    simulation_id: str
    summary: LinkBudgetSummary
    text_report: str = ""
    waterfall_plot: PlotData | None = None


class MaxDataRateResponse(BaseModel):
    simulation_id: str
    max_data_rate_bps: float
    max_data_rate_kbps: float
    link_closes: bool


class RequiredPowerResponse(BaseModel):
    simulation_id: str
    required_power_dbw: float
    required_power_dbm: float
    required_power_w: float


class PassSummary(BaseModel):
    pass_number: int
    start_time_s: float
    end_time_s: float
    duration_s: float
    max_elevation_deg: float
    min_margin_db: float
    max_margin_db: float
    data_volume_bits: float
    data_volume_kbytes: float


class SimulationSummary(BaseModel):
    num_passes: int
    total_contact_time_s: float
    passes_per_day: float
    total_data_volume_bits: float
    total_data_volume_mbytes: float
    avg_pass_duration_s: float
    frequency_hz: float
    data_rate_bps: float


class PassSimulationResponse(BaseModel):
    """Response from pass simulation."""

    simulation_id: str
    summary: SimulationSummary
    passes: list[PassSummary] = Field(default_factory=list)
    text_report: str = ""
    plots: list[PlotData] = Field(default_factory=list)


class ComponentInfo(BaseModel):
    name: str
    category: str
    highlights: dict[str, Any] = Field(default_factory=dict)


class ComponentListResponse(BaseModel):
    category: str
    components: list[ComponentInfo]


class ComponentDetailResponse(BaseModel):
    name: str
    category: str
    data: dict[str, Any]


class PresetInfo(BaseModel):
    name: str
    description: str = ""


class PresetListResponse(BaseModel):
    presets: list[PresetInfo]
