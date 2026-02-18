"""Tests for ITU-R P.838 / P.618 / P.839 rain attenuation models."""

import math

import pytest

from satlinkbudget.atmosphere._rain import (
    effective_rain_height_km,
    rain_attenuation_exceeded,
    rain_specific_attenuation,
    rain_specific_attenuation_coefficients,
)


# ── P.838 coefficients ───────────────────────────────────────────────────


class TestRainCoefficients:
    def test_known_frequency_12ghz(self):
        """At 12 GHz (Ku-band), k and alpha should match the table."""
        k, alpha = rain_specific_attenuation_coefficients(12.0)
        # Circular polarisation (45 deg tilt) is average of H and V
        assert k == pytest.approx(0.0178, rel=0.1)
        assert 1.1 < alpha < 1.4

    def test_known_frequency_30ghz(self):
        """At 30 GHz (Ka-band), k should be around 0.17-0.19."""
        k, alpha = rain_specific_attenuation_coefficients(30.0)
        assert 0.15 < k < 0.22
        assert 0.9 < alpha < 1.1

    def test_k_increases_with_frequency(self):
        """k should generally increase with frequency."""
        freqs = [4.0, 8.0, 12.0, 20.0, 30.0, 50.0]
        ks = [rain_specific_attenuation_coefficients(f)[0] for f in freqs]
        assert all(ks[i] < ks[i + 1] for i in range(len(ks) - 1))

    def test_horizontal_vs_vertical_k(self):
        """k for horizontal polarisation >= k for vertical at most freqs."""
        for f in [8.0, 12.0, 20.0, 30.0]:
            k_h, _ = rain_specific_attenuation_coefficients(f, polarization_tilt_deg=0.0)
            k_v, _ = rain_specific_attenuation_coefficients(f, polarization_tilt_deg=90.0)
            assert k_h >= k_v * 0.95  # H generally >= V (with tolerance)

    def test_raises_on_negative_freq(self):
        """Negative frequency raises ValueError."""
        with pytest.raises(ValueError, match="freq_ghz must be positive"):
            rain_specific_attenuation_coefficients(-5.0)


# ── Specific attenuation gamma_R ──────────────────────────────────────────


class TestRainSpecificAttenuation:
    def test_zero_rain_zero_attenuation(self):
        """No rain → no attenuation."""
        gamma = rain_specific_attenuation(12.0, 0.0)
        assert gamma == 0.0

    def test_increases_with_rain_rate(self):
        """Higher rain rate → more specific attenuation."""
        gamma_light = rain_specific_attenuation(12.0, 5.0)
        gamma_heavy = rain_specific_attenuation(12.0, 50.0)
        assert gamma_heavy > gamma_light > 0.0

    def test_increases_with_frequency(self):
        """At a given rain rate, higher frequency → more attenuation."""
        gamma_ku = rain_specific_attenuation(12.0, 25.0)
        gamma_ka = rain_specific_attenuation(30.0, 25.0)
        assert gamma_ka > gamma_ku

    def test_ku_band_25mmh(self):
        """Ku-band (12 GHz) at 25 mm/h: ~2-5 dB/km (ballpark)."""
        gamma = rain_specific_attenuation(12.0, 25.0)
        assert 1.0 < gamma < 10.0

    def test_always_positive_for_positive_rain(self):
        """gamma_R > 0 whenever R > 0."""
        for f in [4.0, 12.0, 30.0, 50.0]:
            assert rain_specific_attenuation(f, 10.0) > 0.0


# ── P.839 effective rain height ───────────────────────────────────────────


class TestEffectiveRainHeight:
    def test_equatorial(self):
        """At the equator, rain height is 5 km."""
        assert effective_rain_height_km(0.0) == 5.0

    def test_tropical(self):
        """Within 23 deg latitude, rain height is 5 km."""
        assert effective_rain_height_km(20.0) == 5.0
        assert effective_rain_height_km(-15.0) == 5.0

    def test_decreases_with_latitude(self):
        """Rain height decreases with |latitude| above 23 deg."""
        h_30 = effective_rain_height_km(30.0)
        h_50 = effective_rain_height_km(50.0)
        h_70 = effective_rain_height_km(70.0)
        assert h_30 > h_50 > h_70

    def test_symmetric_hemispheres(self):
        """Northern and southern hemispheres give the same result."""
        assert effective_rain_height_km(45.0) == effective_rain_height_km(-45.0)

    def test_non_negative(self):
        """Rain height never goes negative."""
        for lat in range(0, 91, 5):
            assert effective_rain_height_km(lat) >= 0.0


# ── P.618 rain attenuation exceeded 0.01 % ──────────────────────────────


class TestRainAttenuationExceeded:
    def test_zero_rain_zero_attenuation(self):
        """No rain → zero attenuation."""
        a = rain_attenuation_exceeded(12.0, 30.0, 0.0, 45.0)
        assert a == 0.0

    def test_positive_result(self):
        """A typical case should give positive attenuation."""
        a = rain_attenuation_exceeded(12.0, 30.0, 25.0, 45.0)
        assert a > 0.0

    def test_increases_with_rain_rate(self):
        """More rain → more attenuation."""
        a_light = rain_attenuation_exceeded(12.0, 30.0, 10.0, 45.0)
        a_heavy = rain_attenuation_exceeded(12.0, 30.0, 80.0, 45.0)
        assert a_heavy > a_light

    def test_increases_with_frequency(self):
        """Higher frequency → more rain attenuation."""
        a_ku = rain_attenuation_exceeded(12.0, 30.0, 25.0, 45.0)
        a_ka = rain_attenuation_exceeded(30.0, 30.0, 25.0, 45.0)
        assert a_ka > a_ku

    def test_lower_elevation_more_loss(self):
        """Lower elevation → longer slant path → more loss."""
        a_low = rain_attenuation_exceeded(12.0, 10.0, 25.0, 45.0)
        a_high = rain_attenuation_exceeded(12.0, 60.0, 25.0, 45.0)
        assert a_low > a_high

    def test_station_above_rain_height(self):
        """If station is above the rain height, no rain attenuation."""
        a = rain_attenuation_exceeded(12.0, 30.0, 25.0, 45.0, altitude_km=10.0)
        assert a == 0.0
