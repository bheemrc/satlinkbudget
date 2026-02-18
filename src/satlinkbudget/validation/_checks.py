"""Validation checks for link budget parameters."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from satlinkbudget.rf._path_loss import slant_range, free_space_path_loss_db
from satlinkbudget.budget._transmitter import TransmitterChain
from satlinkbudget.budget._receiver import ReceiverChain
from satlinkbudget.budget._link import compute_link_budget


@dataclass
class ValidationResult:
    """Result of a validation check."""

    valid: bool
    message: str


def validate_frequency_band(
    frequency_hz: float, band_min_hz: float, band_max_hz: float
) -> ValidationResult:
    """Check if frequency is within allocated band."""
    if band_min_hz <= frequency_hz <= band_max_hz:
        return ValidationResult(True, "Frequency within allocated band")
    return ValidationResult(
        False,
        f"Frequency {frequency_hz/1e6:.1f} MHz outside band "
        f"[{band_min_hz/1e6:.1f}, {band_max_hz/1e6:.1f}] MHz",
    )


def validate_eirp_limit(
    eirp_dbw: float, max_eirp_dbw: float
) -> ValidationResult:
    """Check if EIRP is within regulatory limits."""
    if eirp_dbw <= max_eirp_dbw:
        return ValidationResult(True, f"EIRP {eirp_dbw:.1f} dBW within limit")
    return ValidationResult(
        False,
        f"EIRP {eirp_dbw:.1f} dBW exceeds limit of {max_eirp_dbw:.1f} dBW",
    )


def validate_link_closes(
    transmitter: TransmitterChain,
    receiver: ReceiverChain,
    frequency_hz: float,
    altitude_m: float,
    data_rate_bps: float,
    required_eb_n0_db: float,
    min_elevation_deg: float = 5.0,
    atmospheric_loss_db: float = 0.0,
) -> ValidationResult:
    """Check if link closes at worst-case geometry (minimum elevation)."""
    dist = slant_range(altitude_m, min_elevation_deg)
    result = compute_link_budget(
        transmitter=transmitter,
        receiver=receiver,
        frequency_hz=frequency_hz,
        distance_m=dist,
        data_rate_bps=data_rate_bps,
        required_eb_n0_db=required_eb_n0_db,
        atmospheric_loss_db=atmospheric_loss_db,
    )
    if result.link_closes:
        return ValidationResult(True, f"Link closes with {result.margin_db:.1f} dB margin at {min_elevation_deg}° elevation")
    return ValidationResult(
        False,
        f"Link does NOT close at {min_elevation_deg}° elevation: margin = {result.margin_db:.1f} dB",
    )


def validate_antenna_gain(
    gain_dbi: float, frequency_hz: float, max_reasonable_gain_dbi: float = 80.0
) -> ValidationResult:
    """Check if antenna gain is physically reasonable for the frequency."""
    if gain_dbi < -10.0:
        return ValidationResult(False, f"Antenna gain {gain_dbi:.1f} dBi is unreasonably low")
    if gain_dbi > max_reasonable_gain_dbi:
        return ValidationResult(False, f"Antenna gain {gain_dbi:.1f} dBi exceeds reasonable maximum")
    return ValidationResult(True, f"Antenna gain {gain_dbi:.1f} dBi is reasonable")


def validate_data_rate(
    data_rate_bps: float, bandwidth_hz: float, spectral_efficiency: float
) -> ValidationResult:
    """Check if data rate is achievable with given bandwidth."""
    max_rate = bandwidth_hz * spectral_efficiency
    if data_rate_bps <= max_rate:
        return ValidationResult(True, f"Data rate {data_rate_bps:.0f} bps achievable with {bandwidth_hz:.0f} Hz bandwidth")
    return ValidationResult(
        False,
        f"Data rate {data_rate_bps:.0f} bps exceeds achievable {max_rate:.0f} bps "
        f"with {bandwidth_hz:.0f} Hz and spectral efficiency {spectral_efficiency:.2f}",
    )
