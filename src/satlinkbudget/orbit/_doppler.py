"""Doppler shift calculations."""

import numpy as np

from satlinkbudget.rf._constants import C_LIGHT, MU_EARTH, R_EARTH


def radial_velocity(
    sat_pos: np.ndarray,
    sat_vel: np.ndarray,
    gs_pos: np.ndarray,
    gs_vel: np.ndarray | None = None,
) -> float:
    """Radial velocity between satellite and ground station [m/s].

    Positive = satellite moving away (receding).

    Parameters
    ----------
    sat_pos : np.ndarray
        Satellite position [m].
    sat_vel : np.ndarray
        Satellite velocity [m/s].
    gs_pos : np.ndarray
        Ground station position [m].
    gs_vel : np.ndarray, optional
        Ground station velocity [m/s]. Zero if None.
    """
    range_vec = sat_pos - gs_pos
    range_unit = range_vec / np.linalg.norm(range_vec)

    rel_vel = sat_vel
    if gs_vel is not None:
        rel_vel = sat_vel - gs_vel

    return float(np.dot(rel_vel, range_unit))


def doppler_shift(frequency_hz: float, v_radial_m_s: float) -> float:
    """Doppler frequency shift [Hz].

    Δf = -f · v_r / c
    Negative v_r (approaching) → positive Δf (blue shift).
    """
    return -frequency_hz * v_radial_m_s / C_LIGHT


def max_doppler_shift(altitude_m: float, frequency_hz: float) -> float:
    """Maximum Doppler shift for a LEO satellite [Hz].

    Worst case occurs near horizon where radial velocity is maximum.
    v_max ≈ v_orbital (at horizon, nearly all velocity is radial).
    """
    r = R_EARTH + altitude_m
    v_orbital = np.sqrt(MU_EARTH / r)
    return frequency_hz * v_orbital / C_LIGHT
