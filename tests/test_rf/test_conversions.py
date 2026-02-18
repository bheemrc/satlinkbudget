"""Tests for RF unit conversions."""

import math

import numpy as np
import pytest

from satlinkbudget.rf._conversions import (
    dbm_to_watts,
    dbw_to_watts,
    frequency_to_wavelength,
    from_db,
    to_db,
    watts_to_dbm,
    watts_to_dbw,
    wavelength_to_frequency,
)
from satlinkbudget.rf._constants import C_LIGHT


class TestToDb:
    def test_unity(self):
        assert to_db(1.0) == pytest.approx(0.0)

    def test_double(self):
        assert to_db(2.0) == pytest.approx(3.0103, rel=1e-3)

    def test_half(self):
        assert to_db(0.5) == pytest.approx(-3.0103, rel=1e-3)

    def test_ten(self):
        assert to_db(10.0) == pytest.approx(10.0)

    def test_hundred(self):
        assert to_db(100.0) == pytest.approx(20.0)

    def test_thousand(self):
        assert to_db(1000.0) == pytest.approx(30.0)


class TestFromDb:
    def test_zero(self):
        assert from_db(0.0) == pytest.approx(1.0)

    def test_ten(self):
        assert from_db(10.0) == pytest.approx(10.0)

    def test_twenty(self):
        assert from_db(20.0) == pytest.approx(100.0)

    def test_negative(self):
        assert from_db(-3.0103) == pytest.approx(0.5, rel=1e-3)


class TestDbRoundtrip:
    @pytest.mark.parametrize("val", [0.001, 0.1, 1.0, 10.0, 100.0, 1e6])
    def test_roundtrip(self, val):
        assert from_db(to_db(val)) == pytest.approx(val, rel=1e-10)


class TestWattsDbw:
    def test_one_watt(self):
        assert watts_to_dbw(1.0) == pytest.approx(0.0)

    def test_ten_watts(self):
        assert watts_to_dbw(10.0) == pytest.approx(10.0)

    def test_milliwatt(self):
        assert watts_to_dbw(0.001) == pytest.approx(-30.0)

    def test_roundtrip(self):
        assert dbw_to_watts(watts_to_dbw(5.0)) == pytest.approx(5.0, rel=1e-10)


class TestWattsDbm:
    def test_one_watt(self):
        assert watts_to_dbm(1.0) == pytest.approx(30.0)

    def test_one_milliwatt(self):
        assert watts_to_dbm(0.001) == pytest.approx(0.0)

    def test_dbm_to_watts(self):
        assert dbm_to_watts(0.0) == pytest.approx(0.001)

    def test_dbm_to_watts_30(self):
        assert dbm_to_watts(30.0) == pytest.approx(1.0)

    def test_roundtrip(self):
        assert dbm_to_watts(watts_to_dbm(0.5)) == pytest.approx(0.5, rel=1e-10)

    def test_dbw_dbm_consistency(self):
        """dBm = dBW + 30."""
        w = 2.5
        assert watts_to_dbm(w) == pytest.approx(watts_to_dbw(w) + 30.0)


class TestFrequencyWavelength:
    def test_one_ghz(self):
        """1 GHz → 0.3 m wavelength."""
        wl = frequency_to_wavelength(1e9)
        assert wl == pytest.approx(C_LIGHT / 1e9, rel=1e-6)
        assert wl == pytest.approx(0.2998, rel=1e-3)

    def test_uhf_437mhz(self):
        wl = frequency_to_wavelength(437e6)
        assert wl == pytest.approx(0.686, rel=1e-2)

    def test_x_band_8ghz(self):
        wl = frequency_to_wavelength(8.2e9)
        assert wl == pytest.approx(0.03656, rel=1e-3)

    def test_roundtrip(self):
        f = 2.4e9
        assert wavelength_to_frequency(frequency_to_wavelength(f)) == pytest.approx(
            f, rel=1e-10
        )
