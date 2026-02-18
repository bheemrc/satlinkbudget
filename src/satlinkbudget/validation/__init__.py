"""Compatibility and validation checks."""

from satlinkbudget.validation._checks import (
    validate_frequency_band,
    validate_eirp_limit,
    validate_link_closes,
    validate_antenna_gain,
    validate_data_rate,
    ValidationResult,
)

__all__ = [
    "validate_frequency_band",
    "validate_eirp_limit",
    "validate_link_closes",
    "validate_antenna_gain",
    "validate_data_rate",
    "ValidationResult",
]
