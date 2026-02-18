"""ITU-R P.676 simplified gaseous (oxygen + water vapor) absorption model.

Provides specific attenuation coefficients for dry air (oxygen) and water
vapor, plus a slant-path integration using equivalent atmospheric heights.
"""

from __future__ import annotations

import math

# ---------------------------------------------------------------------------
# Oxygen (dry air) specific attenuation  [dB/km]
# ---------------------------------------------------------------------------

def specific_attenuation_oxygen(
    freq_ghz: float,
    pressure_hpa: float = 1013.25,
    temp_k: float = 288.15,
) -> float:
    """Specific attenuation due to dry air (oxygen) [dB/km].

    Simplified model based on Liebe (1985) / ITU-R P.676 with:
    - Low-frequency wing (f < 57 GHz): smooth function with
      resonance contribution from the 60-GHz complex and the
      isolated 118.75-GHz line.
    - 57-63 GHz strong absorption complex (~15 dB/km peak at sea level).
    - Decline above the 60-GHz complex toward the 118.75-GHz line.

    Parameters
    ----------
    freq_ghz : float
        Frequency in GHz (must be > 0).
    pressure_hpa : float
        Total atmospheric pressure [hPa] (default: sea level 1013.25).
    temp_k : float
        Absolute temperature [K] (default: 288.15 K = 15 deg C).

    Returns
    -------
    float
        Specific attenuation gamma_o [dB/km].  Always >= 0.
    """
    if freq_ghz <= 0.0:
        raise ValueError("freq_ghz must be positive")

    f = freq_ghz
    p = pressure_hpa / 1013.25  # normalised pressure
    theta = 288.15 / temp_k  # inverse normalised temperature

    if f < 57.0:
        # Simplified Liebe model for the low-frequency wing
        gamma = (
            7.2 * f**2 / (f**2 + 0.34**2)
            + 0.62 * f**2 / ((54.0 - f) ** 2 + 0.6**2)
        ) * 1.0e-3 * p * theta**0.8

        # Add 118.75 GHz line contribution (minor at these frequencies)
        gamma += (
            0.015 * f**2 / ((118.75 - f) ** 2 + 1.0**2)
        ) * 1.0e-3 * p * theta**0.8

    elif f <= 63.0:
        # 57-63 GHz strong absorption complex
        # Model as a broad peak centered at 60 GHz
        peak = 15.0 * p * theta**0.8
        sigma = 3.0  # half-width in GHz
        gamma = peak * math.exp(-((f - 60.0) ** 2) / (2.0 * sigma**2))
        # Floor: even at the edges of this band attenuation is significant
        edge_min = 1.0 * p * theta**0.8
        gamma = max(gamma, edge_min)

    elif f <= 120.0:
        # Decline from 60-GHz complex toward 118.75-GHz isolated line
        # Contribution from the tail of the 60-GHz complex
        tail_60 = 0.5 * math.exp(-((f - 60.0) ** 2) / 200.0)
        # Contribution from the 118.75-GHz line
        line_118 = 0.30 / ((f - 118.75) ** 2 + 1.0**2)
        gamma = (tail_60 + line_118 + 3.0e-3 * f) * p * theta**0.8

    else:
        # Above 120 GHz – gentle increase with frequency
        tail_118 = 0.30 / ((f - 118.75) ** 2 + 1.0**2)
        gamma = (tail_118 + 3.5e-3 * f) * p * theta**0.8

    return max(gamma, 0.0)


# ---------------------------------------------------------------------------
# Water-vapor specific attenuation  [dB/km]
# ---------------------------------------------------------------------------

def specific_attenuation_water_vapor(
    freq_ghz: float,
    rho_g_m3: float = 7.5,
    pressure_hpa: float = 1013.25,
    temp_k: float = 288.15,
) -> float:
    """Specific attenuation due to water vapor [dB/km].

    Simplified model capturing the principal resonance lines at
    22.235 GHz, 183.31 GHz, and 325.153 GHz.

    Parameters
    ----------
    freq_ghz : float
        Frequency in GHz (must be > 0).
    rho_g_m3 : float
        Water-vapor density [g/m^3] (default: 7.5).
    pressure_hpa : float
        Total atmospheric pressure [hPa].
    temp_k : float
        Absolute temperature [K].

    Returns
    -------
    float
        Specific attenuation gamma_w [dB/km].  Always >= 0.
    """
    if freq_ghz <= 0.0:
        raise ValueError("freq_ghz must be positive")
    if rho_g_m3 < 0.0:
        raise ValueError("rho_g_m3 must be non-negative")

    f = freq_ghz
    rho = rho_g_m3

    if rho == 0.0:
        return 0.0

    # Spectral line contributions (Lorentzian shapes)
    gamma_w = (
        0.050
        + 0.0021 * rho
        + 3.6 / ((f - 22.235) ** 2 + 8.5)
        + 10.6 / ((f - 183.31) ** 2 + 9.0)
        + 8.9 / ((f - 325.153) ** 2 + 26.3)
    ) * f**2 * rho * 1.0e-4

    return max(gamma_w, 0.0)


# ---------------------------------------------------------------------------
# Total gaseous attenuation along a slant path  [dB]
# ---------------------------------------------------------------------------

_H_DRY_KM = 6.0   # equivalent height, dry atmosphere [km]
_H_WET_KM = 2.1   # equivalent height, wet (water-vapor) [km]
_MIN_ELEVATION = 5.0  # minimum elevation angle [degrees]


def gaseous_attenuation_slant(
    freq_ghz: float,
    elevation_deg: float,
    pressure_hpa: float = 1013.25,
    temp_k: float = 288.15,
    rho_g_m3: float = 7.5,
) -> float:
    """Total gaseous attenuation along the slant path [dB].

    Uses the equivalent-height model::

        A = (gamma_o * h_o + gamma_w * h_w) / sin(El)

    where h_o ~ 6 km (dry) and h_w ~ 2.1 km (wet).
    Elevation is clamped to a minimum of 5 degrees.

    Parameters
    ----------
    freq_ghz : float
        Frequency [GHz].
    elevation_deg : float
        Elevation angle above the local horizon [degrees].
    pressure_hpa : float
        Total atmospheric pressure [hPa].
    temp_k : float
        Absolute temperature [K].
    rho_g_m3 : float
        Surface water-vapor density [g/m^3].

    Returns
    -------
    float
        Total gaseous attenuation [dB].  Always >= 0.
    """
    if freq_ghz <= 0.0:
        raise ValueError("freq_ghz must be positive")

    el = max(elevation_deg, _MIN_ELEVATION)
    sin_el = math.sin(math.radians(el))

    gamma_o = specific_attenuation_oxygen(freq_ghz, pressure_hpa, temp_k)
    gamma_w = specific_attenuation_water_vapor(freq_ghz, rho_g_m3, pressure_hpa, temp_k)

    zenith_atten = gamma_o * _H_DRY_KM + gamma_w * _H_WET_KM
    return max(zenith_atten / sin_el, 0.0)
