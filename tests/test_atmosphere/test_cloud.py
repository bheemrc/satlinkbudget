"""Tests for ITU-R P.840 cloud and fog attenuation model."""

import pytest

from satlinkbudget.atmosphere._cloud import (
    cloud_attenuation,
    cloud_specific_attenuation_coefficient,
)


class TestCloudSpecificAttenuationCoefficient:
    def test_positive(self):
        """K_l is always positive for positive frequency."""
        for f in [1.0, 10.0, 30.0, 100.0]:
            assert cloud_specific_attenuation_coefficient(f) > 0.0

    def test_increases_with_frequency(self):
        """K_l increases with frequency (Rayleigh regime, roughly f^2)."""
        freqs = [5.0, 10.0, 20.0, 30.0, 50.0]
        kls = [cloud_specific_attenuation_coefficient(f) for f in freqs]
        assert all(kls[i] < kls[i + 1] for i in range(len(kls) - 1))

    def test_reasonable_at_ku_band(self):
        """At Ku-band (12 GHz) K_l ~ 0.1 - 0.5 (dB/km)/(g/m3) range."""
        kl = cloud_specific_attenuation_coefficient(12.0)
        assert 0.05 < kl < 1.0

    def test_reasonable_at_ka_band(self):
        """At Ka-band (30 GHz) K_l should be larger than at Ku-band."""
        kl_ku = cloud_specific_attenuation_coefficient(12.0)
        kl_ka = cloud_specific_attenuation_coefficient(30.0)
        assert kl_ka > kl_ku

    def test_temperature_dependence(self):
        """Warmer cloud → different K_l (permittivity changes with T)."""
        kl_cold = cloud_specific_attenuation_coefficient(30.0, temp_k=260.0)
        kl_warm = cloud_specific_attenuation_coefficient(30.0, temp_k=290.0)
        # Both should be positive and different
        assert kl_cold > 0.0
        assert kl_warm > 0.0
        assert kl_cold != pytest.approx(kl_warm, rel=0.01)

    def test_raises_on_negative_freq(self):
        """Negative frequency raises ValueError."""
        with pytest.raises(ValueError, match="freq_ghz must be positive"):
            cloud_specific_attenuation_coefficient(-1.0)


class TestCloudAttenuation:
    def test_zero_lwc_zero_attenuation(self):
        """Zero liquid water content → zero attenuation."""
        a = cloud_attenuation(30.0, 30.0, liquid_water_content_kg_m2=0.0)
        assert a == 0.0

    def test_positive_for_positive_lwc(self):
        """Positive LWC → positive cloud attenuation."""
        a = cloud_attenuation(30.0, 30.0, liquid_water_content_kg_m2=0.3)
        assert a > 0.0

    def test_increases_with_lwc(self):
        """More liquid water → more attenuation."""
        a_low = cloud_attenuation(30.0, 30.0, liquid_water_content_kg_m2=0.1)
        a_high = cloud_attenuation(30.0, 30.0, liquid_water_content_kg_m2=1.0)
        assert a_high > a_low

    def test_lower_elevation_more_loss(self):
        """Lower elevation → longer path → more cloud attenuation."""
        a_low = cloud_attenuation(30.0, 10.0, liquid_water_content_kg_m2=0.3)
        a_high = cloud_attenuation(30.0, 60.0, liquid_water_content_kg_m2=0.3)
        assert a_low > a_high

    def test_elevation_clamped_at_5deg(self):
        """Elevations below 5 deg are clamped."""
        a_1 = cloud_attenuation(30.0, 1.0, liquid_water_content_kg_m2=0.3)
        a_5 = cloud_attenuation(30.0, 5.0, liquid_water_content_kg_m2=0.3)
        assert a_1 == pytest.approx(a_5, rel=1e-10)

    def test_ka_band_typical_value(self):
        """Ka-band (30 GHz) with 0.3 kg/m2 at 30 deg: reasonable range."""
        a = cloud_attenuation(30.0, 30.0, liquid_water_content_kg_m2=0.3)
        # Expect a few tenths of a dB to a few dB
        assert 0.01 < a < 5.0
