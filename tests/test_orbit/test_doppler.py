"""Tests for Doppler shift calculations."""

import numpy as np
import pytest

from satlinkbudget.orbit._doppler import (
    radial_velocity,
    doppler_shift,
    max_doppler_shift,
)


class TestRadialVelocity:
    def test_approaching(self):
        """Satellite moving toward GS → negative radial velocity."""
        sat_pos = np.array([1000.0, 0.0, 0.0])
        sat_vel = np.array([-100.0, 0.0, 0.0])
        gs_pos = np.array([0.0, 0.0, 0.0])
        v_r = radial_velocity(sat_pos, sat_vel, gs_pos)
        assert v_r < 0

    def test_receding(self):
        """Satellite moving away from GS → positive radial velocity."""
        sat_pos = np.array([1000.0, 0.0, 0.0])
        sat_vel = np.array([100.0, 0.0, 0.0])
        gs_pos = np.array([0.0, 0.0, 0.0])
        v_r = radial_velocity(sat_pos, sat_vel, gs_pos)
        assert v_r > 0

    def test_perpendicular(self):
        """Velocity perpendicular to range → zero radial velocity."""
        sat_pos = np.array([1000.0, 0.0, 0.0])
        sat_vel = np.array([0.0, 100.0, 0.0])
        gs_pos = np.array([0.0, 0.0, 0.0])
        v_r = radial_velocity(sat_pos, sat_vel, gs_pos)
        assert v_r == pytest.approx(0.0, abs=1e-10)

    def test_with_gs_velocity(self):
        """GS velocity reduces relative radial velocity."""
        sat_pos = np.array([1000.0, 0.0, 0.0])
        sat_vel = np.array([100.0, 0.0, 0.0])
        gs_pos = np.array([0.0, 0.0, 0.0])
        gs_vel = np.array([50.0, 0.0, 0.0])
        v_r = radial_velocity(sat_pos, sat_vel, gs_pos, gs_vel)
        assert v_r == pytest.approx(50.0, abs=1e-6)


class TestDopplerShift:
    def test_approaching_blue_shift(self):
        """Approaching → positive frequency shift."""
        df = doppler_shift(437e6, -7500.0)  # approaching at 7.5 km/s
        assert df > 0

    def test_receding_red_shift(self):
        """Receding → negative frequency shift."""
        df = doppler_shift(437e6, 7500.0)
        assert df < 0

    def test_zero_velocity(self):
        """Zero radial velocity → no shift."""
        assert doppler_shift(437e6, 0.0) == 0.0

    def test_uhf_magnitude(self):
        """UHF 437 MHz at 7.5 km/s → ~10.9 kHz shift."""
        df = abs(doppler_shift(437e6, 7500.0))
        assert df == pytest.approx(10930, abs=200)


class TestMaxDopplerShift:
    def test_uhf_500km(self):
        """Max Doppler at UHF (437 MHz), 500 km → ~11 kHz."""
        max_df = max_doppler_shift(500e3, 437e6)
        assert 9000 < max_df < 13000

    def test_increases_with_frequency(self):
        df_uhf = max_doppler_shift(500e3, 437e6)
        df_s = max_doppler_shift(500e3, 2.2e9)
        assert df_s > df_uhf

    def test_decreases_with_altitude(self):
        """Higher altitude → lower orbital velocity → less Doppler."""
        df_low = max_doppler_shift(400e3, 437e6)
        df_high = max_doppler_shift(800e3, 437e6)
        assert df_low > df_high

    def test_positive(self):
        assert max_doppler_shift(500e3, 437e6) > 0
