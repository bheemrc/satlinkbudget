"""System noise temperature, noise figure, G/T, antenna noise."""

import numpy as np

from satlinkbudget.rf._constants import T_REF


def system_noise_temperature(
    t_ant_k: float,
    t_lna_k: float,
    g_lna_db: float,
    t_subsequent_k: float = 0.0,
) -> float:
    """System noise temperature using Friis formula.

    T_sys = T_ant + T_lna + T_subsequent / G_lna

    Parameters
    ----------
    t_ant_k : float
        Antenna noise temperature [K].
    t_lna_k : float
        LNA noise temperature [K].
    g_lna_db : float
        LNA gain [dB].
    t_subsequent_k : float
        Noise temperature of subsequent stages [K].

    Returns
    -------
    float
        System noise temperature [K].
    """
    g_lna_linear = 10.0 ** (g_lna_db / 10.0)
    return t_ant_k + t_lna_k + t_subsequent_k / g_lna_linear


def noise_figure_to_temperature(nf_db: float) -> float:
    """Convert noise figure [dB] to equivalent noise temperature [K].

    T = T_ref · (10^(NF/10) - 1)
    """
    return T_REF * (10.0 ** (nf_db / 10.0) - 1.0)


def figure_of_merit_db(gain_db: float, t_sys_k: float) -> float:
    """Receiver figure of merit G/T [dB/K].

    G/T = G_dB - 10·log₁₀(T_sys)
    """
    return gain_db - 10.0 * np.log10(t_sys_k)


def antenna_noise_temperature(
    frequency_hz: float, elevation_deg: float
) -> float:
    """Estimate antenna noise temperature from sky + ground spillover.

    Simplified model: sky noise decreases with frequency (cosmic background),
    ground contribution decreases with elevation (less spillover at zenith).

    Parameters
    ----------
    frequency_hz : float
        Frequency [Hz].
    elevation_deg : float
        Elevation angle [deg].

    Returns
    -------
    float
        Estimated antenna noise temperature [K].
    """
    freq_ghz = frequency_hz / 1e9

    # Sky noise: dominant at low freq, cosmic background ~3K at high freq
    if freq_ghz < 0.1:
        t_sky = 10000.0  # Galactic noise dominant
    elif freq_ghz < 1.0:
        # Galactic noise falls ~f^-2.5
        t_sky = 10000.0 * (freq_ghz / 0.1) ** (-2.5)
    elif freq_ghz < 10.0:
        # Quiet sky 3-20 K
        t_sky = 20.0 * (freq_ghz / 1.0) ** (-0.5)
    else:
        # Atmospheric emission rises above 10 GHz
        t_sky = 3.0 + 2.0 * (freq_ghz / 10.0) ** 1.5

    # Ground noise contribution: ~290K weighted by fraction of beam on ground
    # Higher elevation = less ground pickup
    el_rad = np.radians(max(elevation_deg, 5.0))
    ground_fraction = 0.1 * (1.0 - np.sin(el_rad))  # ~10% sidelobe at horizon
    t_ground = 290.0 * ground_fraction

    return t_sky + t_ground


def rain_noise_temperature(
    rain_atten_db: float, rain_temp_k: float = 275.0
) -> float:
    """Noise temperature increase due to rain.

    T_rain = T_medium · (1 - 10^(-A_rain/10))

    Parameters
    ----------
    rain_atten_db : float
        Rain attenuation [dB].
    rain_temp_k : float
        Physical temperature of rain medium [K].

    Returns
    -------
    float
        Additional noise temperature due to rain [K].
    """
    return rain_temp_k * (1.0 - 10.0 ** (-rain_atten_db / 10.0))
