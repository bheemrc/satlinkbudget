"""ITU-R P.531 ionospheric scintillation model.

Provides the S4 scintillation index and the corresponding fade depth
for a given percentage of time.
"""

from __future__ import annotations

import math


def scintillation_index_s4(
    freq_ghz: float,
    geomagnetic_latitude_deg: float = 45.0,
    solar_flux_index: float = 120.0,
    local_time_hours: float = 14.0,
) -> float:
    """ITU-R P.531 ionospheric scintillation index S4.

    S4 characterises the intensity fluctuation of a signal traversing the
    ionosphere.  Key dependencies:

    - Frequency: S4 proportional to f^{-1.5} (strong at VHF/UHF,
      negligible above ~4 GHz).
    - Solar activity: increases with the 10.7 cm solar flux index.
    - Geomagnetic latitude: strongest in equatorial (|lat| < 20 deg) and
      auroral (|lat| > 55 deg) zones; weakest at mid-latitudes.
    - Local time: peaks around 20:00-01:00 local time (post-sunset).

    Parameters
    ----------
    freq_ghz : float
        Frequency [GHz] (must be > 0).
    geomagnetic_latitude_deg : float
        Geomagnetic latitude [degrees] (default: 45 = mid-latitude).
    solar_flux_index : float
        10.7 cm solar flux index (default: 120, moderate activity).
    local_time_hours : float
        Local solar time [hours, 0-24] (default: 14 = daytime).

    Returns
    -------
    float
        S4 index (dimensionless, 0 to ~1+).
    """
    if freq_ghz <= 0.0:
        raise ValueError("freq_ghz must be positive")

    # Frequency scaling: S4 ~ (1.5 GHz / f)^1.5 referenced to L-band
    f_ref = 1.5  # reference frequency [GHz]
    freq_factor = (f_ref / freq_ghz) ** 1.5

    # Solar activity scaling (normalised to moderate activity = 120)
    solar_factor = (solar_flux_index / 120.0) ** 0.5

    # Geomagnetic latitude factor: equatorial and auroral peaks
    lat = abs(geomagnetic_latitude_deg)
    if lat <= 20.0:
        # Equatorial zone — strong scintillation
        lat_factor = 1.0
    elif lat <= 55.0:
        # Mid-latitude trough — weak scintillation
        lat_factor = 0.1 + 0.9 * math.exp(-((lat - 20.0) ** 2) / 200.0)
    else:
        # Auroral zone — moderate to strong
        lat_factor = 0.3 + 0.7 * math.exp(-((lat - 65.0) ** 2) / 100.0)

    # Local-time factor: peak around 21:00 local (post-sunset)
    hour_offset = local_time_hours - 21.0
    if hour_offset < -12.0:
        hour_offset += 24.0
    elif hour_offset > 12.0:
        hour_offset -= 24.0
    time_factor = 0.2 + 0.8 * math.exp(-(hour_offset**2) / 18.0)

    # Base S4 at reference frequency under moderate conditions
    s4_base = 0.6

    s4 = s4_base * freq_factor * solar_factor * lat_factor * time_factor
    return max(s4, 0.0)


def ionospheric_scintillation_loss(
    freq_ghz: float,
    elevation_deg: float,
    geomagnetic_latitude_deg: float = 45.0,
    solar_flux_index: float = 120.0,
    local_time_hours: float = 14.0,
    percentage: float = 1.0,
) -> float:
    """Ionospheric scintillation fade depth [dB].

    Converts the S4 scintillation index to a fade depth exceeded for
    *percentage* % of the time, using the Nakagami-m distribution
    approximation.

    Significant below ~4 GHz; negligible at X-band and above.

    Parameters
    ----------
    freq_ghz : float
        Frequency [GHz].
    elevation_deg : float
        Elevation angle [degrees] (clamped to >= 5 deg).
    geomagnetic_latitude_deg : float
        Geomagnetic latitude [degrees].
    solar_flux_index : float
        10.7 cm solar flux index.
    local_time_hours : float
        Local solar time [hours].
    percentage : float
        Percentage of time the fade is exceeded (e.g. 1.0 for 1 %).

    Returns
    -------
    float
        Scintillation fade depth [dB].  Always >= 0.
    """
    if freq_ghz <= 0.0:
        raise ValueError("freq_ghz must be positive")

    s4 = scintillation_index_s4(
        freq_ghz, geomagnetic_latitude_deg, solar_flux_index, local_time_hours
    )

    if s4 < 1.0e-6:
        return 0.0

    # Elevation scaling: obliquity factor F(El) ~ 1/sqrt(sin(El))
    el = max(elevation_deg, 5.0)
    obliquity = 1.0 / math.sqrt(math.sin(math.radians(el)))

    # Nakagami-m parameter from S4
    # m = 1 / S4^2 (for weak-to-moderate scintillation)
    s4_eff = min(s4 * obliquity, 2.0)  # cap to avoid singularities

    if s4_eff < 1.0e-6:
        return 0.0

    # Fade depth approximation [dB]:
    # For a Nakagami channel the fade exceeded for p% relates to the
    # complementary CDF.  Simplified: fade_dB ~ -5*log10(1 - S4 * q)
    # where q depends on the percentage.
    # A practical approximation widely used:
    #   fade_dB = 27.5 * S4^1.26 * (-ln(p/100))^0.45   (for p < 50%)
    if percentage <= 0.0 or percentage >= 100.0:
        raise ValueError("percentage must be between 0 and 100 (exclusive)")

    fade = 27.5 * s4_eff**1.26 * (-math.log(percentage / 100.0)) ** 0.45

    return max(fade, 0.0)
