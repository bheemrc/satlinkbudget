"""Tests for free-space path loss and slant range."""

import numpy as np
import pytest

from satlinkbudget.rf._path_loss import free_space_path_loss_db, slant_range
from satlinkbudget.rf._constants import R_EARTH


class TestFreeSpacePathLoss:
    def test_known_1ghz_1000km(self):
        """1 GHz at 1000 km: 32.45 + 60 + 60 = 152.45 dB."""
        fspl = free_space_path_loss_db(1000e3, 1e9)
        assert fspl == pytest.approx(152.44, abs=0.2)

    def test_known_2ghz_36000km(self):
        """GEO at S-band: 32.45 + 66.0 + 91.1 ≈ 189.6 dB."""
        fspl = free_space_path_loss_db(36000e3, 2e9)
        assert fspl == pytest.approx(189.6, abs=0.3)

    def test_double_distance_6db(self):
        """Doubling distance adds ~6 dB."""
        fspl1 = free_space_path_loss_db(1000e3, 1e9)
        fspl2 = free_space_path_loss_db(2000e3, 1e9)
        assert (fspl2 - fspl1) == pytest.approx(6.02, abs=0.1)

    def test_double_frequency_6db(self):
        """Doubling frequency adds ~6 dB."""
        fspl1 = free_space_path_loss_db(1000e3, 1e9)
        fspl2 = free_space_path_loss_db(1000e3, 2e9)
        assert (fspl2 - fspl1) == pytest.approx(6.02, abs=0.1)

    def test_positive(self):
        """FSPL is always positive (loss)."""
        assert free_space_path_loss_db(100.0, 1e6) > 0

    def test_increases_with_distance(self):
        """FSPL monotonically increases with distance."""
        distances = [100e3, 500e3, 1000e3, 5000e3]
        losses = [free_space_path_loss_db(d, 1e9) for d in distances]
        assert all(losses[i] < losses[i + 1] for i in range(len(losses) - 1))

    def test_increases_with_frequency(self):
        """FSPL monotonically increases with frequency."""
        freqs = [100e6, 500e6, 1e9, 10e9]
        losses = [free_space_path_loss_db(1000e3, f) for f in freqs]
        assert all(losses[i] < losses[i + 1] for i in range(len(losses) - 1))


class TestSlantRange:
    def test_zenith(self):
        """At 90° elevation, slant range equals altitude."""
        alt = 500e3
        sr = slant_range(alt, 90.0)
        assert sr == pytest.approx(alt, rel=1e-6)

    def test_horizon_maximum(self):
        """At 0° elevation, slant range is maximum."""
        alt = 500e3
        sr_0 = slant_range(alt, 0.0)
        sr_90 = slant_range(alt, 90.0)
        assert sr_0 > sr_90

    def test_decreases_with_elevation(self):
        """Slant range decreases monotonically with elevation."""
        alt = 500e3
        elevations = [5, 15, 30, 45, 60, 75, 90]
        ranges = [slant_range(alt, el) for el in elevations]
        assert all(ranges[i] > ranges[i + 1] for i in range(len(ranges) - 1))

    def test_greater_than_altitude(self):
        """Slant range is always ≥ altitude (equality only at zenith)."""
        alt = 500e3
        for el in [5, 10, 20, 45, 89]:
            assert slant_range(alt, el) > alt

    def test_leo_500km_horizon(self):
        """500 km LEO at 5° elevation → ~1800-2300 km slant range."""
        sr = slant_range(500e3, 5.0)
        assert 1800e3 < sr < 2300e3

    def test_leo_500km_45deg(self):
        """500 km LEO at 45° → ~600-700 km slant range."""
        sr = slant_range(500e3, 45.0)
        assert 580e3 < sr < 720e3

    def test_geo_orbit(self):
        """GEO at 5° elevation → ~40,000-42,000 km."""
        sr = slant_range(35786e3, 5.0)
        assert 40000e3 < sr < 42000e3
