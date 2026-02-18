"""Free-space path loss and slant range geometry."""

import numpy as np

from satlinkbudget.rf._constants import C_LIGHT, R_EARTH


def free_space_path_loss_db(distance_m: float, frequency_hz: float) -> float:
    """Free-space path loss in dB.

    FSPL = 20·log₁₀(4πdf/c)

    Parameters
    ----------
    distance_m : float
        Distance between transmitter and receiver [m].
    frequency_hz : float
        Carrier frequency [Hz].

    Returns
    -------
    float
        Path loss in dB (positive value).
    """
    return float(
        20.0 * np.log10(4.0 * np.pi * distance_m * frequency_hz / C_LIGHT)
    )


def slant_range(altitude_m: float, elevation_deg: float) -> float:
    """Slant range from ground station to satellite.

    Geometric computation assuming spherical Earth.

    Parameters
    ----------
    altitude_m : float
        Satellite altitude above Earth surface [m].
    elevation_deg : float
        Elevation angle from ground station [deg].

    Returns
    -------
    float
        Slant range [m].
    """
    el_rad = np.radians(elevation_deg)
    r_sat = R_EARTH + altitude_m

    # Law of cosines approach
    # d = -R_E·sin(el) + sqrt((R_E·sin(el))² + r_sat² - R_E²)
    sin_el = np.sin(el_rad)
    return float(
        -R_EARTH * sin_el
        + np.sqrt((R_EARTH * sin_el) ** 2 + r_sat**2 - R_EARTH**2)
    )
