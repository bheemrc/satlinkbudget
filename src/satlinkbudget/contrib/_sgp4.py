"""SGP4 TLE-based orbit adapter.

Wraps the sgp4 library to provide an orbit object compatible with
satlinkbudget's ``find_contacts`` and ``PassSimulation``.

Install: ``pip install sgp4>=2.20``
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

try:
    from sgp4.api import Satrec, WGS72
    HAS_SGP4 = True
except ImportError:
    HAS_SGP4 = False

from satlinkbudget.orbit._propagator import OrbitState
from satlinkbudget.rf._constants import MU_EARTH, R_EARTH


@dataclass
class SGP4Orbit:
    """Orbit adapter backed by SGP4 TLE propagation.

    Provides the same ``propagate(time_s)`` interface as
    :class:`satlinkbudget.orbit.Orbit` so it can be used with
    ``find_contacts`` and ``PassSimulation``.

    Parameters
    ----------
    satrec : Satrec
        sgp4 satellite record.
    epoch_jd : float
        Julian date of the epoch (fractional part added from fr).
    epoch_fr : float
        Fractional day part of the epoch.
    """

    satrec: object  # Satrec, but typed as object for when sgp4 is missing
    epoch_jd: float
    epoch_fr: float

    @property
    def altitude_m(self) -> float:
        """Approximate mean altitude [m] from mean motion."""
        if not HAS_SGP4:
            return 0.0
        # n is in rad/min in sgp4
        n_rad_s = self.satrec.no_kozai / 60.0  # type: ignore[union-attr]
        a = (MU_EARTH / n_rad_s**2) ** (1.0 / 3.0)
        return a - R_EARTH

    @property
    def period_s(self) -> float:
        """Orbital period [s] from mean motion."""
        if not HAS_SGP4:
            return 0.0
        n_rad_s = self.satrec.no_kozai / 60.0  # type: ignore[union-attr]
        return 2.0 * np.pi / n_rad_s

    def propagate(self, time_s: float) -> OrbitState:
        """Propagate to *time_s* seconds since epoch.

        Returns an :class:`OrbitState` with ECI position [m] and
        velocity [m/s].
        """
        if not HAS_SGP4:
            raise RuntimeError("sgp4 is not installed")

        # sgp4 expects minutes since epoch
        minutes = time_s / 60.0

        # sgp4 returns km and km/s
        e, r, v = self.satrec.sgp4(self.epoch_jd, self.epoch_fr + minutes / 1440.0)  # type: ignore[union-attr]
        if e != 0:
            raise RuntimeError(f"SGP4 propagation error code {e}")

        pos_m = np.array(r) * 1e3
        vel_m_s = np.array(v) * 1e3

        return OrbitState(time_s=time_s, position_eci=pos_m, velocity_eci=vel_m_s)


def orbit_from_tle(line1: str, line2: str) -> SGP4Orbit:
    """Create an SGP4Orbit from Two-Line Element strings.

    Parameters
    ----------
    line1 : str
        TLE line 1.
    line2 : str
        TLE line 2.

    Returns
    -------
    SGP4Orbit
        Orbit adapter that can be used with ``find_contacts``.

    Raises
    ------
    ImportError
        If sgp4 is not installed.

    Example
    -------
    >>> orbit = orbit_from_tle(line1, line2)
    >>> state = orbit.propagate(0.0)
    >>> print(state.position_eci)
    """
    if not HAS_SGP4:
        raise ImportError(
            "sgp4 is required for TLE propagation. "
            "Install with: pip install sgp4>=2.20"
        )

    sat = Satrec.twoline2rv(line1, line2, WGS72)
    return SGP4Orbit(
        satrec=sat,
        epoch_jd=sat.jdsatepoch,
        epoch_fr=sat.jdsatepochF,
    )
