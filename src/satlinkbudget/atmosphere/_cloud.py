"""ITU-R P.840 cloud and fog attenuation model.

Provides the specific attenuation coefficient K_l for cloud liquid water
and the total cloud/fog attenuation along a slant path.
"""

from __future__ import annotations

import math


def cloud_specific_attenuation_coefficient(
    freq_ghz: float,
    temp_k: float = 273.15,
) -> float:
    """P.840 cloud liquid-water specific-attenuation coefficient K_l.

    Returns K_l in [dB/km per g/m^3].  This uses a simplified Rayleigh
    approximation that grows roughly as f^1.7-2 below ~100 GHz.

    The temperature dependence enters via the Debye relaxation model for
    the complex permittivity of water.  The simplified expression used
    here captures the dominant behaviour.

    Parameters
    ----------
    freq_ghz : float
        Frequency [GHz] (must be > 0).
    temp_k : float
        Cloud / fog temperature [K] (default: 273.15 K = 0 deg C).

    Returns
    -------
    float
        K_l [dB/km / (g/m^3)].  Always >= 0.
    """
    if freq_ghz <= 0.0:
        raise ValueError("freq_ghz must be positive")

    f = freq_ghz

    # Debye relaxation model for liquid water
    # Primary relaxation frequency [GHz]
    theta = 300.0 / temp_k
    fp = 20.20 - 146.4 * (theta - 1.0) + 316.0 * (theta - 1.0) ** 2
    # Secondary relaxation frequency [GHz]
    fs = 39.8 * fp

    # Static and high-frequency permittivities
    eps_0 = 77.66 + 103.3 * (theta - 1.0)
    eps_1 = 0.0671 * eps_0
    eps_2 = 3.52

    # Complex permittivity components (real and imaginary parts)
    # eps = eps' - j * eps''
    # eps' = (eps_0 - eps_1)/(1 + (f/fp)^2) + (eps_1 - eps_2)/(1 + (f/fs)^2) + eps_2
    # eps'' = f*(eps_0 - eps_1)/(fp*(1 + (f/fp)^2)) + f*(eps_1 - eps_2)/(fs*(1 + (f/fs)^2))

    term1_denom = 1.0 + (f / fp) ** 2
    term2_denom = 1.0 + (f / fs) ** 2

    eps_real = (
        (eps_0 - eps_1) / term1_denom
        + (eps_1 - eps_2) / term2_denom
        + eps_2
    )
    eps_imag = (
        f * (eps_0 - eps_1) / (fp * term1_denom)
        + f * (eps_1 - eps_2) / (fs * term2_denom)
    )

    # Rayleigh approximation: K_l = 0.819 * f / (eps'' * (1 + eta^2))
    # where eta = (2 + eps') / eps''
    eta = (2.0 + eps_real) / eps_imag if eps_imag > 0.0 else 1.0e30
    k_l = 0.819 * f / (eps_imag * (1.0 + eta**2))

    return max(k_l, 0.0)


def cloud_attenuation(
    freq_ghz: float,
    elevation_deg: float,
    liquid_water_content_kg_m2: float = 0.3,
    temp_k: float = 273.15,
) -> float:
    """Total cloud / fog attenuation along the slant path [dB].

    A_cloud = K_l * L / sin(El)

    where L is the columnar liquid-water content [kg/m^2] and K_l is in
    [(dB/km) / (g/m^3)].  Since 1 kg/m^2 of columnar water spread over
    1 km gives 1 g/m^3, K_l * L has units of dB directly for a vertical
    path.

    Parameters
    ----------
    freq_ghz : float
        Frequency [GHz].
    elevation_deg : float
        Elevation angle [degrees] (clamped to >= 5 deg).
    liquid_water_content_kg_m2 : float
        Total columnar liquid-water content [kg/m^2] (default: 0.3).
    temp_k : float
        Cloud temperature [K].

    Returns
    -------
    float
        Cloud attenuation [dB].  Always >= 0.
    """
    if liquid_water_content_kg_m2 <= 0.0:
        return 0.0

    el = max(elevation_deg, 5.0)
    sin_el = math.sin(math.radians(el))

    k_l = cloud_specific_attenuation_coefficient(freq_ghz, temp_k)
    return max(k_l * liquid_water_content_kg_m2 / sin_el, 0.0)
