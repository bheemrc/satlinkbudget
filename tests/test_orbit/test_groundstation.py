"""Tests for ground station model."""

import numpy as np
import pytest

from satlinkbudget.orbit._groundstation import (
    GroundStation,
    elevation_angle,
)
from satlinkbudget.rf._constants import R_EARTH


class TestGroundStation:
    def test_ecef_equator(self):
        """Station on equator at 0° lon → (R_E, 0, 0)."""
        gs = GroundStation("test", 0.0, 0.0)
        pos = gs.ecef_position()
        assert pos[0] == pytest.approx(R_EARTH, rel=1e-6)
        assert abs(pos[1]) < 1.0
        assert abs(pos[2]) < 1.0

    def test_ecef_north_pole(self):
        """Station at north pole → (0, 0, R_E)."""
        gs = GroundStation("pole", 90.0, 0.0)
        pos = gs.ecef_position()
        assert abs(pos[0]) < 1.0
        assert abs(pos[1]) < 1.0
        assert pos[2] == pytest.approx(R_EARTH, rel=1e-6)

    def test_eci_at_zero_gmst(self):
        """At GMST=0, ECI = ECEF."""
        gs = GroundStation("test", 45.0, 30.0)
        ecef = gs.ecef_position()
        eci = gs.eci_position(0.0)
        np.testing.assert_allclose(ecef, eci, atol=1.0)

    def test_from_datasheet(self):
        gs = GroundStation.from_datasheet("ksat_svalbard")
        assert gs.latitude_deg == pytest.approx(78.23)
        assert gs.name == "KSAT Svalbard"


class TestElevationAngle:
    def test_zenith_pass(self):
        """Satellite directly above → 90° elevation."""
        gs_pos = np.array([R_EARTH, 0.0, 0.0])
        sat_pos = np.array([R_EARTH + 500e3, 0.0, 0.0])
        el = elevation_angle(sat_pos, gs_pos)
        assert el == pytest.approx(90.0, abs=0.5)

    def test_far_away_negative(self):
        """Satellite on opposite side of Earth → negative elevation."""
        gs_pos = np.array([R_EARTH, 0.0, 0.0])
        sat_pos = np.array([-R_EARTH - 500e3, 0.0, 0.0])
        el = elevation_angle(sat_pos, gs_pos)
        assert el < 0

    def test_elevation_symmetric(self):
        """Satellites at equal angular offsets should have same elevation."""
        gs_pos = np.array([R_EARTH, 0.0, 0.0])
        r = R_EARTH + 500e3
        angle = np.radians(10.0)
        sat1 = np.array([r * np.cos(angle), r * np.sin(angle), 0.0])
        sat2 = np.array([r * np.cos(angle), -r * np.sin(angle), 0.0])
        el1 = elevation_angle(sat1, gs_pos)
        el2 = elevation_angle(sat2, gs_pos)
        assert el1 == pytest.approx(el2, abs=0.1)

    def test_elevation_range(self):
        """Elevation should be in [-90, 90]."""
        gs_pos = np.array([R_EARTH, 0.0, 0.0])
        for angle in range(0, 360, 30):
            a = np.radians(angle)
            sat_pos = np.array([
                (R_EARTH + 500e3) * np.cos(a),
                (R_EARTH + 500e3) * np.sin(a),
                0.0,
            ])
            el = elevation_angle(sat_pos, gs_pos)
            assert -90 <= el <= 90
