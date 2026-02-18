"""Tests for the SGP4 contrib adapter."""

import numpy as np
import pytest

sgp4_api = pytest.importorskip("sgp4.api", reason="sgp4 not installed")

from satlinkbudget.contrib._sgp4 import SGP4Orbit, orbit_from_tle, HAS_SGP4


# ISS TLE (valid structure, real epoch not critical for tests)
LINE1 = "1 25544U 98067A   24001.50000000  .00016717  00000-0  10270-3 0  9006"
LINE2 = "2 25544  51.6400 300.0000 0006000  50.0000 310.0000 15.49560000400000"


class TestSGP4Flag:
    def test_has_sgp4_true(self):
        assert HAS_SGP4 is True


class TestOrbitFromTLE:
    def test_creates_orbit(self):
        orbit = orbit_from_tle(LINE1, LINE2)
        assert isinstance(orbit, SGP4Orbit)

    def test_epoch_fields(self):
        orbit = orbit_from_tle(LINE1, LINE2)
        assert orbit.epoch_jd > 0
        assert isinstance(orbit.epoch_fr, float)

    def test_altitude_reasonable(self):
        orbit = orbit_from_tle(LINE1, LINE2)
        alt_km = orbit.altitude_m / 1e3
        # ISS orbits at ~400-420 km
        assert 300 < alt_km < 500

    def test_period_reasonable(self):
        orbit = orbit_from_tle(LINE1, LINE2)
        period_min = orbit.period_s / 60.0
        # ISS period ~92 min
        assert 85 < period_min < 100


class TestSGP4OrbitPropagate:
    def test_propagate_returns_orbit_state(self):
        orbit = orbit_from_tle(LINE1, LINE2)
        state = orbit.propagate(0.0)
        assert state.time_s == 0.0
        assert state.position_eci.shape == (3,)
        assert state.velocity_eci.shape == (3,)

    def test_propagate_position_magnitude(self):
        orbit = orbit_from_tle(LINE1, LINE2)
        state = orbit.propagate(0.0)
        r = np.linalg.norm(state.position_eci)
        r_km = r / 1e3
        # Earth radius (~6378 km) + altitude (~420 km) = ~6798 km
        assert 6500 < r_km < 7200

    def test_propagate_velocity_magnitude(self):
        orbit = orbit_from_tle(LINE1, LINE2)
        state = orbit.propagate(0.0)
        v = np.linalg.norm(state.velocity_eci)
        # LEO orbital velocity ~7.5 km/s
        assert 7000 < v < 8000

    def test_propagate_different_times(self):
        orbit = orbit_from_tle(LINE1, LINE2)
        s1 = orbit.propagate(0.0)
        s2 = orbit.propagate(600.0)  # 10 minutes later
        # Position should differ
        delta = np.linalg.norm(s2.position_eci - s1.position_eci)
        assert delta > 1e3  # moved at least 1 km

    def test_propagate_one_orbit(self):
        orbit = orbit_from_tle(LINE1, LINE2)
        s1 = orbit.propagate(0.0)
        s2 = orbit.propagate(orbit.period_s)
        # After one orbit, position should be close to start (but not exact due to J2)
        delta_km = np.linalg.norm(s2.position_eci - s1.position_eci) / 1e3
        assert delta_km < 200  # within ~200 km after one orbit
