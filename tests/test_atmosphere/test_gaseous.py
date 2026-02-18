"""Tests for ITU-R P.676 gaseous absorption (oxygen + water vapor)."""

import math

import pytest

from satlinkbudget.atmosphere._gaseous import (
    gaseous_attenuation_slant,
    specific_attenuation_oxygen,
    specific_attenuation_water_vapor,
)


# ── Oxygen specific attenuation ──────────────────────────────────────────


class TestSpecificAttenuationOxygen:
    def test_negligible_at_1ghz(self):
        """At 1 GHz oxygen absorption is very small (< 0.01 dB/km)."""
        gamma = specific_attenuation_oxygen(1.0)
        assert 0.0 < gamma < 0.01

    def test_moderate_at_10ghz(self):
        """At 10 GHz absorption is small but non-negligible."""
        gamma = specific_attenuation_oxygen(10.0)
        assert 0.001 < gamma < 0.02

    def test_strong_peak_at_60ghz(self):
        """The 60-GHz oxygen absorption complex: > 10 dB/km at sea level."""
        gamma = specific_attenuation_oxygen(60.0)
        assert gamma > 10.0

    def test_peak_region_57_to_63ghz_high(self):
        """Entire 57-63 GHz band should show strong absorption (> 1 dB/km)."""
        for f in [57.0, 59.0, 60.0, 61.0, 63.0]:
            gamma = specific_attenuation_oxygen(f)
            assert gamma > 1.0, f"Expected > 1 dB/km at {f} GHz, got {gamma}"

    def test_118_75ghz_line(self):
        """There is a secondary peak near 118.75 GHz."""
        gamma_118 = specific_attenuation_oxygen(118.75)
        gamma_100 = specific_attenuation_oxygen(100.0)
        assert gamma_118 > gamma_100

    def test_always_positive(self):
        """Oxygen attenuation is non-negative at all frequencies."""
        for f in [0.5, 1.0, 5.0, 22.0, 40.0, 60.0, 100.0, 200.0]:
            assert specific_attenuation_oxygen(f) >= 0.0

    def test_pressure_dependence(self):
        """Higher pressure increases absorption (linear to first order)."""
        gamma_sea = specific_attenuation_oxygen(10.0, pressure_hpa=1013.25)
        gamma_alt = specific_attenuation_oxygen(10.0, pressure_hpa=700.0)
        assert gamma_sea > gamma_alt

    def test_temperature_dependence(self):
        """Lower temperature (higher theta) slightly increases absorption."""
        gamma_cold = specific_attenuation_oxygen(10.0, temp_k=250.0)
        gamma_hot = specific_attenuation_oxygen(10.0, temp_k=310.0)
        assert gamma_cold > gamma_hot

    def test_raises_on_negative_freq(self):
        """Negative frequency should raise ValueError."""
        with pytest.raises(ValueError, match="freq_ghz must be positive"):
            specific_attenuation_oxygen(-1.0)


# ── Water-vapor specific attenuation ─────────────────────────────────────


class TestSpecificAttenuationWaterVapor:
    def test_peak_near_22ghz(self):
        """Water-vapor has a resonance near 22.235 GHz."""
        gamma_22 = specific_attenuation_water_vapor(22.235)
        gamma_15 = specific_attenuation_water_vapor(15.0)
        gamma_30 = specific_attenuation_water_vapor(30.0)
        assert gamma_22 > gamma_15
        assert gamma_22 > gamma_30

    def test_increases_with_humidity(self):
        """More water vapor → more attenuation."""
        gamma_dry = specific_attenuation_water_vapor(22.0, rho_g_m3=3.0)
        gamma_wet = specific_attenuation_water_vapor(22.0, rho_g_m3=15.0)
        assert gamma_wet > gamma_dry

    def test_zero_humidity(self):
        """Zero water-vapor density → zero attenuation."""
        gamma = specific_attenuation_water_vapor(22.0, rho_g_m3=0.0)
        assert gamma == 0.0

    def test_always_positive(self):
        """Water-vapor attenuation is non-negative."""
        for f in [1.0, 10.0, 22.0, 50.0, 183.0, 325.0]:
            assert specific_attenuation_water_vapor(f, rho_g_m3=7.5) >= 0.0

    def test_183ghz_peak(self):
        """Water-vapor has a strong resonance near 183.31 GHz."""
        gamma_183 = specific_attenuation_water_vapor(183.31)
        gamma_150 = specific_attenuation_water_vapor(150.0)
        assert gamma_183 > gamma_150


# ── Gaseous attenuation slant path ───────────────────────────────────────


class TestGaseousAttenuationSlant:
    def test_positive_at_typical_conditions(self):
        """Slant-path gaseous attenuation should be positive."""
        atten = gaseous_attenuation_slant(12.0, 30.0)
        assert atten > 0.0

    def test_lower_elevation_more_loss(self):
        """Lower elevation → longer path → more loss."""
        atten_low = gaseous_attenuation_slant(12.0, 10.0)
        atten_high = gaseous_attenuation_slant(12.0, 45.0)
        assert atten_low > atten_high

    def test_elevation_clamped_at_5deg(self):
        """Elevations below 5 deg are clamped to 5 deg."""
        atten_1 = gaseous_attenuation_slant(12.0, 1.0)
        atten_5 = gaseous_attenuation_slant(12.0, 5.0)
        assert atten_1 == pytest.approx(atten_5, rel=1e-10)

    def test_zenith_equals_vertical_integral(self):
        """At 90 deg elevation, A = gamma_o * h_o + gamma_w * h_w."""
        freq = 22.0
        atten = gaseous_attenuation_slant(freq, 90.0)
        gamma_o = specific_attenuation_oxygen(freq)
        gamma_w = specific_attenuation_water_vapor(freq)
        expected = gamma_o * 6.0 + gamma_w * 2.1
        assert atten == pytest.approx(expected, rel=1e-6)

    def test_60ghz_very_high_attenuation(self):
        """At 60 GHz the gaseous attenuation is extremely high."""
        atten = gaseous_attenuation_slant(60.0, 30.0)
        # 60 GHz: gamma_o ~ 15 dB/km, h_o = 6 km → zenith ~90 dB
        # at 30 deg el: ~180 dB — satellite link is essentially blocked
        assert atten > 50.0
