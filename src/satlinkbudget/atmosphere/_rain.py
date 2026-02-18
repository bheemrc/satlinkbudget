"""ITU-R P.838 / P.618 / P.839 rain attenuation models.

Provides:
- Specific attenuation coefficients k and alpha (P.838).
- Specific rain attenuation gamma_R = k * R^alpha.
- Effective rain height (P.839).
- Slant-path rain attenuation exceeded for 0.01 % of an average year (P.618).
"""

from __future__ import annotations

import math

import numpy as np

# ---------------------------------------------------------------------------
# P.838 tabulated coefficients for horizontal (H) and vertical (V)
# polarisations.  We interpolate in log-space.
# ---------------------------------------------------------------------------

_FREQ_TABLE = np.array([1.0, 4.0, 8.0, 12.0, 20.0, 30.0, 50.0, 100.0])

_K_H_TABLE = np.array(
    [0.0000387, 0.00065, 0.00454, 0.0188, 0.0751, 0.187, 0.536, 1.31]
)
_ALPHA_H_TABLE = np.array([0.912, 1.121, 1.327, 1.276, 1.099, 1.021, 0.826, 0.616])

_K_V_TABLE = np.array(
    [0.0000352, 0.00053, 0.00395, 0.0168, 0.0691, 0.167, 0.479, 1.17]
)
_ALPHA_V_TABLE = np.array([0.880, 1.075, 1.310, 1.264, 1.065, 0.979, 0.759, 0.545])

_LOG_FREQ = np.log10(_FREQ_TABLE)
_LOG_KH = np.log10(_K_H_TABLE)
_LOG_KV = np.log10(_K_V_TABLE)


def _interp_log(x: float, xp: np.ndarray, fp: np.ndarray) -> float:
    """Linear interpolation (with extrapolation) in log10(f) space."""
    return float(np.interp(math.log10(x), xp, fp))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def rain_specific_attenuation_coefficients(
    freq_ghz: float,
    elevation_deg: float = 0.0,
    polarization_tilt_deg: float = 45.0,
) -> tuple[float, float]:
    """P.838 rain specific-attenuation coefficients *k* and *alpha*.

    The polarisation-dependent values are obtained by interpolating log10(k)
    and alpha from tabulated horizontal and vertical data, then combining
    for the effective polarisation tilt angle *tau*::

        k = (k_H + k_V + (k_H - k_V) * cos^2(El) * cos(2*tau)) / 2
        alpha = (k_H*a_H + k_V*a_V + (k_H*a_H - k_V*a_V)*cos^2(El)*cos(2*tau)) / (2*k)

    Parameters
    ----------
    freq_ghz : float
        Frequency [GHz] (valid range roughly 1 - 100 GHz).
    elevation_deg : float
        Path elevation angle [degrees].
    polarization_tilt_deg : float
        Polarisation tilt angle relative to horizontal [degrees].
        0 = H, 90 = V, 45 = circular (default).

    Returns
    -------
    tuple[float, float]
        (k, alpha)
    """
    if freq_ghz <= 0.0:
        raise ValueError("freq_ghz must be positive")

    # Interpolate H and V in log(f) space
    log_kh = _interp_log(freq_ghz, _LOG_FREQ, _LOG_KH)
    k_h = 10.0**log_kh
    alpha_h = _interp_log(freq_ghz, _LOG_FREQ, _ALPHA_H_TABLE)

    log_kv = _interp_log(freq_ghz, _LOG_FREQ, _LOG_KV)
    k_v = 10.0**log_kv
    alpha_v = _interp_log(freq_ghz, _LOG_FREQ, _ALPHA_V_TABLE)

    # Combine for effective polarisation
    el_rad = math.radians(elevation_deg)
    tau_rad = math.radians(polarization_tilt_deg)
    cos2_el = math.cos(el_rad) ** 2
    cos_2tau = math.cos(2.0 * tau_rad)

    k = (k_h + k_v + (k_h - k_v) * cos2_el * cos_2tau) / 2.0
    alpha_num = (
        k_h * alpha_h
        + k_v * alpha_v
        + (k_h * alpha_h - k_v * alpha_v) * cos2_el * cos_2tau
    )
    alpha = alpha_num / (2.0 * k) if k > 0.0 else (alpha_h + alpha_v) / 2.0

    return k, alpha


def rain_specific_attenuation(
    freq_ghz: float,
    rain_rate_mm_h: float,
    elevation_deg: float = 0.0,
    polarization_tilt_deg: float = 45.0,
) -> float:
    """Specific attenuation due to rain [dB/km].

    gamma_R = k * R^alpha

    Parameters
    ----------
    freq_ghz : float
        Frequency [GHz].
    rain_rate_mm_h : float
        Rain rate [mm/h].
    elevation_deg : float
        Path elevation angle [degrees].
    polarization_tilt_deg : float
        Polarisation tilt angle [degrees].

    Returns
    -------
    float
        gamma_R [dB/km].  Returns 0.0 when rain_rate is 0.
    """
    if rain_rate_mm_h <= 0.0:
        return 0.0

    k, alpha = rain_specific_attenuation_coefficients(
        freq_ghz, elevation_deg, polarization_tilt_deg
    )
    return k * rain_rate_mm_h**alpha


def effective_rain_height_km(latitude_deg: float) -> float:
    """ITU-R P.839 mean annual rain height above mean sea level [km].

    Simplified latitude-dependent model:
    - |lat| <= 23 deg  : h_R = 5.0 km
    - |lat|  > 23 deg  : h_R = 5.0 - 0.075 * (|lat| - 23), clamped >= 0

    Parameters
    ----------
    latitude_deg : float
        Station latitude [degrees] (positive = N, negative = S).

    Returns
    -------
    float
        Mean rain height [km].
    """
    lat = abs(latitude_deg)
    if lat <= 23.0:
        return 5.0
    h_r = 5.0 - 0.075 * (lat - 23.0)
    return max(h_r, 0.0)


def rain_attenuation_exceeded(
    freq_ghz: float,
    elevation_deg: float,
    rain_rate_001_mm_h: float,
    latitude_deg: float,
    altitude_km: float = 0.0,
    polarization_tilt_deg: float = 45.0,
) -> float:
    """P.618 rain attenuation exceeded for 0.01 % of time [dB].

    Procedure:
    1. Rain height h_R from P.839.
    2. Slant-path length L_s = (h_R - h_s) / sin(El)  (El >= 5 deg).
    3. Horizontal projection L_G = L_s * cos(El).
    4. Specific attenuation gamma_R.
    5. Reduction factor r_001.
    6. A_001 = gamma_R * L_s * r_001.

    Parameters
    ----------
    freq_ghz : float
        Frequency [GHz].
    elevation_deg : float
        Elevation angle [degrees] (clamped to >= 5 deg internally).
    rain_rate_001_mm_h : float
        Rain rate exceeded 0.01 % of the time [mm/h].
    latitude_deg : float
        Station latitude [degrees].
    altitude_km : float
        Station altitude above mean sea level [km].
    polarization_tilt_deg : float
        Polarisation tilt angle [degrees].

    Returns
    -------
    float
        Rain attenuation A_001 [dB].  Always >= 0.
    """
    if rain_rate_001_mm_h <= 0.0:
        return 0.0

    h_r = effective_rain_height_km(latitude_deg)
    h_s = altitude_km

    # If rain height is below or at station altitude, no rain path
    if h_r <= h_s:
        return 0.0

    el = max(elevation_deg, 5.0)
    el_rad = math.radians(el)
    sin_el = math.sin(el_rad)
    cos_el = math.cos(el_rad)

    # Slant-path length through rain [km]
    l_s = (h_r - h_s) / sin_el

    # Horizontal projection [km]
    l_g = l_s * cos_el

    # Specific attenuation [dB/km]
    gamma_r = rain_specific_attenuation(
        freq_ghz, rain_rate_001_mm_h, elevation_deg, polarization_tilt_deg
    )

    if gamma_r <= 0.0:
        return 0.0

    # Reduction factor (P.618 step 6)
    r_001 = 1.0 / (
        1.0
        + 0.78 * math.sqrt(l_g * gamma_r / freq_ghz)
        - 0.38 * (1.0 - math.exp(-2.0 * l_g))
    )
    # Clamp reduction factor to (0, 1]
    r_001 = max(min(r_001, 1.0), 0.01)

    a_001 = gamma_r * l_s * r_001
    return max(a_001, 0.0)
