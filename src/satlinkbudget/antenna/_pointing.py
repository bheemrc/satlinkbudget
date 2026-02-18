"""Pointing loss and polarization mismatch calculations."""

import numpy as np


def pointing_loss_db(off_axis_deg: float, beamwidth_3db_deg: float) -> float:
    """Antenna pointing loss [dB].

    Gaussian beam approximation: L = 12 · (θ / BW_3dB)² dB

    Parameters
    ----------
    off_axis_deg : float
        Off-axis angle [degrees].
    beamwidth_3db_deg : float
        3 dB beamwidth [degrees].

    Returns
    -------
    float
        Pointing loss in dB (positive value, represents loss).
    """
    return 12.0 * (off_axis_deg / beamwidth_3db_deg) ** 2


def polarization_mismatch_loss_db(
    tx_polarization: str, rx_polarization: str
) -> float:
    """Polarization mismatch loss [dB].

    Parameters
    ----------
    tx_polarization : str
        Transmitter polarization: "linear_v", "linear_h", "rhcp", "lhcp".
    rx_polarization : str
        Receiver polarization (same options).

    Returns
    -------
    float
        Mismatch loss in dB.
    """
    tx = tx_polarization.lower()
    rx = rx_polarization.lower()

    # Same polarization → 0 dB loss
    if tx == rx:
        return 0.0

    # Cross-polarized linear → infinite loss (use 30 dB practical limit)
    linear_types = {"linear_v", "linear_h"}
    circular_types = {"rhcp", "lhcp"}

    if tx in linear_types and rx in linear_types and tx != rx:
        return 30.0  # Cross-pol isolation, practical limit

    # Counter-rotating circular → infinite loss
    if tx in circular_types and rx in circular_types and tx != rx:
        return 30.0

    # Linear ↔ circular → 3 dB loss
    if (tx in linear_types and rx in circular_types) or (
        tx in circular_types and rx in linear_types
    ):
        return 3.0

    # Unknown combination, assume worst case
    return 3.0
