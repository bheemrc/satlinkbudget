"""Skyfield high-precision ephemeris adapter.

Wraps Skyfield satellite and Topos objects to produce
satlinkbudget-compatible orbit and ground station instances.

Install: ``pip install skyfield>=1.45``
"""

from __future__ import annotations

import numpy as np

try:
    from skyfield.api import EarthSatellite, Topos, load as skyfield_load
    HAS_SKYFIELD = True
except ImportError:
    HAS_SKYFIELD = False

from satlinkbudget.orbit._propagator import OrbitState
from satlinkbudget.orbit._groundstation import GroundStation
from satlinkbudget.rf._constants import R_EARTH, MU_EARTH


class SkyfieldOrbit:
    """Orbit adapter backed by Skyfield EarthSatellite.

    Provides the same ``propagate(time_s)`` interface as
    :class:`satlinkbudget.orbit.Orbit`.

    Parameters
    ----------
    satellite : EarthSatellite
        Skyfield satellite object.
    ts : skyfield timescale
        Skyfield timescale for time conversions.
    """

    def __init__(self, satellite: object, ts: object) -> None:
        self._sat = satellite
        self._ts = ts
        # Cache epoch as a Skyfield Time
        self._epoch = satellite.epoch  # type: ignore[union-attr]

    @property
    def altitude_m(self) -> float:
        """Approximate mean altitude [m]."""
        model = self._sat.model  # type: ignore[union-attr]
        n_rad_s = model.no_kozai / 60.0
        a = (MU_EARTH / n_rad_s**2) ** (1.0 / 3.0)
        return a - R_EARTH

    @property
    def period_s(self) -> float:
        """Orbital period [s]."""
        model = self._sat.model  # type: ignore[union-attr]
        n_rad_s = model.no_kozai / 60.0
        return 2.0 * np.pi / n_rad_s

    def propagate(self, time_s: float) -> OrbitState:
        """Propagate to *time_s* seconds since TLE epoch.

        Returns an :class:`OrbitState` with GCRS (≈ECI) position [m]
        and velocity [m/s].
        """
        if not HAS_SKYFIELD:
            raise RuntimeError("skyfield is not installed")

        # Build time at epoch + time_s
        jd = self._epoch.whole
        fr = self._epoch.tt_fraction + time_s / 86400.0
        t = self._ts.tt_jd(jd + fr)  # type: ignore[union-attr]

        # GCRS position and velocity
        geocentric = self._sat.at(t)  # type: ignore[union-attr]
        pos_km = geocentric.position.km
        vel_km_s = geocentric.velocity.km_per_s

        return OrbitState(
            time_s=time_s,
            position_eci=np.array(pos_km) * 1e3,
            velocity_eci=np.array(vel_km_s) * 1e3,
        )


def orbit_from_skyfield(satellite: object, ts: object) -> SkyfieldOrbit:
    """Create a SkyfieldOrbit adapter from a Skyfield EarthSatellite.

    Parameters
    ----------
    satellite : skyfield.api.EarthSatellite
        Skyfield satellite built from TLE.
    ts : skyfield timescale
        Skyfield timescale (from ``skyfield.api.load.timescale()``).

    Returns
    -------
    SkyfieldOrbit
        Orbit adapter compatible with ``find_contacts`` and ``PassSimulation``.
    """
    if not HAS_SKYFIELD:
        raise ImportError(
            "skyfield is required. Install with: pip install skyfield>=1.45"
        )
    return SkyfieldOrbit(satellite, ts)


def ground_station_from_skyfield(
    name: str,
    topos: object,
    min_elevation_deg: float = 5.0,
) -> GroundStation:
    """Create a GroundStation from a Skyfield Topos object.

    Parameters
    ----------
    name : str
        Human-readable ground station name.
    topos : skyfield.api.Topos
        Skyfield geographic position.
    min_elevation_deg : float
        Minimum elevation for contact [degrees].

    Returns
    -------
    GroundStation
        satlinkbudget GroundStation instance.
    """
    if not HAS_SKYFIELD:
        raise ImportError(
            "skyfield is required. Install with: pip install skyfield>=1.45"
        )

    lat = topos.latitude.degrees  # type: ignore[union-attr]
    lon = topos.longitude.degrees  # type: ignore[union-attr]
    alt_m = topos.elevation.m  # type: ignore[union-attr]

    return GroundStation(
        name=name,
        latitude_deg=lat,
        longitude_deg=lon,
        altitude_m=alt_m,
        min_elevation_deg=min_elevation_deg,
    )
