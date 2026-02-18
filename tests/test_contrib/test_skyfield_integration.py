"""Tests for the Skyfield contrib adapter."""

import numpy as np
import pytest

skyfield_api = pytest.importorskip("skyfield.api", reason="skyfield not installed")

from skyfield.api import EarthSatellite, load, Topos

from satlinkbudget.contrib._skyfield import (
    SkyfieldOrbit,
    orbit_from_skyfield,
    ground_station_from_skyfield,
    HAS_SKYFIELD,
)
from satlinkbudget.orbit._groundstation import GroundStation


# ISS TLE
LINE1 = "1 25544U 98067A   24001.50000000  .00016717  00000-0  10270-3 0  9006"
LINE2 = "2 25544  51.6400 300.0000 0006000  50.0000 310.0000 15.49560000400000"


@pytest.fixture
def ts():
    return load.timescale()


@pytest.fixture
def satellite(ts):
    return EarthSatellite(LINE1, LINE2, "ISS", ts)


class TestSkyfieldFlag:
    def test_has_skyfield_true(self):
        assert HAS_SKYFIELD is True


class TestOrbitFromSkyfield:
    def test_creates_orbit(self, satellite, ts):
        orbit = orbit_from_skyfield(satellite, ts)
        assert isinstance(orbit, SkyfieldOrbit)

    def test_altitude_reasonable(self, satellite, ts):
        orbit = orbit_from_skyfield(satellite, ts)
        alt_km = orbit.altitude_m / 1e3
        assert 300 < alt_km < 500

    def test_period_reasonable(self, satellite, ts):
        orbit = orbit_from_skyfield(satellite, ts)
        period_min = orbit.period_s / 60.0
        assert 85 < period_min < 100

    def test_propagate_returns_state(self, satellite, ts):
        orbit = orbit_from_skyfield(satellite, ts)
        state = orbit.propagate(0.0)
        assert state.time_s == 0.0
        assert state.position_eci.shape == (3,)
        assert state.velocity_eci.shape == (3,)

    def test_propagate_position_magnitude(self, satellite, ts):
        orbit = orbit_from_skyfield(satellite, ts)
        state = orbit.propagate(0.0)
        r_km = np.linalg.norm(state.position_eci) / 1e3
        assert 6500 < r_km < 7200

    def test_propagate_velocity_magnitude(self, satellite, ts):
        orbit = orbit_from_skyfield(satellite, ts)
        state = orbit.propagate(0.0)
        v = np.linalg.norm(state.velocity_eci)
        assert 7000 < v < 8000


class TestGroundStationFromSkyfield:
    def test_creates_ground_station(self):
        topos = Topos(latitude_degrees=78.23, longitude_degrees=15.39, elevation_m=400.0)
        gs = ground_station_from_skyfield("Svalbard", topos)
        assert isinstance(gs, GroundStation)
        assert gs.name == "Svalbard"

    def test_coordinates(self):
        topos = Topos(latitude_degrees=78.23, longitude_degrees=15.39, elevation_m=400.0)
        gs = ground_station_from_skyfield("Svalbard", topos)
        assert abs(gs.latitude_deg - 78.23) < 0.01
        assert abs(gs.longitude_deg - 15.39) < 0.01
        assert abs(gs.altitude_m - 400.0) < 1.0

    def test_min_elevation(self):
        topos = Topos(latitude_degrees=45.0, longitude_degrees=10.0, elevation_m=0.0)
        gs = ground_station_from_skyfield("Test", topos, min_elevation_deg=10.0)
        assert gs.min_elevation_deg == 10.0
