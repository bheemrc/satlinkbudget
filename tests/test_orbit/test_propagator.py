"""Tests for orbit propagator."""

import numpy as np
import pytest

from satlinkbudget.orbit._propagator import Orbit
from satlinkbudget.rf._constants import R_EARTH, MU_EARTH


class TestOrbitPeriod:
    def test_500km_period(self):
        """500 km orbit period ≈ 5677 s."""
        orb = Orbit.circular(500.0, 97.4, j2=False)
        expected = 2 * np.pi * np.sqrt((R_EARTH + 500e3) ** 3 / MU_EARTH)
        assert orb.period_s == pytest.approx(expected, rel=1e-6)
        assert orb.period_s == pytest.approx(5677, abs=10)

    def test_iss_orbit(self):
        """ISS ~420 km ≈ 5580 s period."""
        orb = Orbit.circular(420.0, 51.6, j2=False)
        assert 5500 < orb.period_s < 5700

    def test_higher_altitude_longer_period(self):
        p1 = Orbit.circular(400.0, 45.0).period_s
        p2 = Orbit.circular(800.0, 45.0).period_s
        assert p2 > p1


class TestOrbitPropagation:
    def test_initial_position_magnitude(self):
        """At t=0, satellite at semi_major_axis distance."""
        orb = Orbit.circular(500.0, 97.4, j2=False)
        state = orb.propagate(0.0)
        r = np.linalg.norm(state.position_eci)
        assert r == pytest.approx(R_EARTH + 500e3, rel=1e-6)

    def test_position_magnitude_constant(self):
        """Circular orbit: distance from Earth center is constant."""
        orb = Orbit.circular(500.0, 97.4, j2=False)
        expected_r = R_EARTH + 500e3
        for t in [0, 1000, 2000, 3000]:
            state = orb.propagate(t)
            r = np.linalg.norm(state.position_eci)
            assert r == pytest.approx(expected_r, rel=1e-4)

    def test_one_period_returns(self):
        """After one full period, satellite returns to same position."""
        orb = Orbit.circular(500.0, 0.0, j2=False)
        s0 = orb.propagate(0.0)
        s1 = orb.propagate(orb.period_s)
        np.testing.assert_allclose(
            s0.position_eci, s1.position_eci, atol=1.0
        )

    def test_velocity_magnitude(self):
        """Circular orbit velocity: v = sqrt(mu/r)."""
        orb = Orbit.circular(500.0, 97.4, j2=False)
        state = orb.propagate(0.0)
        v = np.linalg.norm(state.velocity_eci)
        expected_v = np.sqrt(MU_EARTH / (R_EARTH + 500e3))
        assert v == pytest.approx(expected_v, rel=1e-3)

    def test_equatorial_stays_in_plane(self):
        """Equatorial orbit has z ≈ 0 always."""
        orb = Orbit.circular(500.0, 0.0, j2=False)
        for t in [0, 1000, 2838]:
            state = orb.propagate(t)
            assert abs(state.position_eci[2]) < 1.0  # < 1 m

    def test_polar_orbit_reaches_poles(self):
        """90° inclination orbit reaches z = ±(R_E + alt)."""
        orb = Orbit.circular(500.0, 90.0, j2=False)
        # At quarter period, satellite should be near pole
        state = orb.propagate(orb.period_s / 4.0)
        r = R_EARTH + 500e3
        assert abs(state.position_eci[2]) == pytest.approx(r, rel=0.01)

    def test_propagate_array(self):
        orb = Orbit.circular(500.0, 97.4)
        times = np.array([0.0, 100.0, 200.0])
        states = orb.propagate_array(times)
        assert len(states) == 3
        assert states[1].time_s == 100.0


class TestJ2Perturbation:
    def test_j2_raan_drift_retrograde(self):
        """SSO orbit: J2 causes RAAN to drift ~0.9856°/day eastward."""
        orb = Orbit.circular(500.0, 97.4, j2=True)
        # RAAN rate should be positive for SSO (~0.9856°/day)
        rate_deg_per_day = np.degrees(orb.raan_rate) * 86400
        assert rate_deg_per_day == pytest.approx(0.9856, abs=0.1)

    def test_j2_raan_negative_for_prograde(self):
        """Prograde orbit (i < 90°): RAAN drifts westward (negative)."""
        orb = Orbit.circular(500.0, 45.0, j2=True)
        assert orb.raan_rate < 0

    def test_j2_disabled(self):
        """No J2 → no RAAN drift."""
        orb = Orbit.circular(500.0, 97.4, j2=False)
        assert orb.raan_rate == 0.0
