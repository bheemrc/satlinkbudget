"""dB/linear conversions, power unit conversions, frequency/wavelength."""

import numpy as np

from satlinkbudget.rf._constants import C_LIGHT


def to_db(linear: float) -> float:
    """Convert linear ratio to decibels."""
    return float(10.0 * np.log10(linear))


def from_db(db: float) -> float:
    """Convert decibels to linear ratio."""
    return float(10.0 ** (db / 10.0))


def watts_to_dbw(watts: float) -> float:
    """Convert watts to dBW."""
    return float(10.0 * np.log10(watts))


def dbw_to_watts(dbw: float) -> float:
    """Convert dBW to watts."""
    return float(10.0 ** (dbw / 10.0))


def watts_to_dbm(watts: float) -> float:
    """Convert watts to dBm."""
    return float(10.0 * np.log10(watts) + 30.0)


def dbm_to_watts(dbm: float) -> float:
    """Convert dBm to watts."""
    return float(10.0 ** ((dbm - 30.0) / 10.0))


def frequency_to_wavelength(frequency_hz: float) -> float:
    """Convert frequency [Hz] to wavelength [m]."""
    return C_LIGHT / frequency_hz


def wavelength_to_frequency(wavelength_m: float) -> float:
    """Convert wavelength [m] to frequency [Hz]."""
    return C_LIGHT / wavelength_m
