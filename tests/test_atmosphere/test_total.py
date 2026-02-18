"""Tests for the aggregated atmospheric loss computation."""

import pytest

from satlinkbudget.atmosphere._total import (
    AtmosphericLosses,
    compute_atmospheric_losses,
)


class TestAtmosphericLosses:
    def test_total_is_sum(self):
        """total_db equals the sum of individual components."""
        losses = AtmosphericLosses(
            gaseous_db=1.0, rain_db=2.0, cloud_db=0.5, scintillation_db=0.3
        )
        assert losses.total_db == pytest.approx(3.8)

    def test_zero_losses(self):
        """All-zero components → zero total."""
        losses = AtmosphericLosses(
            gaseous_db=0.0, rain_db=0.0, cloud_db=0.0, scintillation_db=0.0
        )
        assert losses.total_db == 0.0


class TestComputeAtmosphericLosses:
    def test_all_components_computed(self):
        """All four components should be computed."""
        losses = compute_atmospheric_losses(
            freq_ghz=12.0,
            elevation_deg=30.0,
            rain_rate_001_mm_h=25.0,
            latitude_deg=45.0,
            liquid_water_content_kg_m2=0.3,
            include_scintillation=True,
            scintillation_percentage=1.0,
        )
        assert losses.gaseous_db > 0.0
        assert losses.rain_db > 0.0
        assert losses.cloud_db > 0.0
        # At 12 GHz mid-lat, scintillation may be very small but non-negative
        assert losses.scintillation_db >= 0.0

    def test_total_is_sum_of_parts(self):
        """total_db property equals the sum of individual fields."""
        losses = compute_atmospheric_losses(
            freq_ghz=30.0,
            elevation_deg=30.0,
            rain_rate_001_mm_h=25.0,
            latitude_deg=45.0,
            liquid_water_content_kg_m2=0.3,
        )
        expected = (
            losses.gaseous_db
            + losses.rain_db
            + losses.cloud_db
            + losses.scintillation_db
        )
        assert losses.total_db == pytest.approx(expected)

    def test_clear_sky_dominated_by_gaseous(self):
        """Clear sky (no rain, no cloud): gaseous should dominate."""
        losses = compute_atmospheric_losses(
            freq_ghz=12.0,
            elevation_deg=30.0,
            rain_rate_001_mm_h=0.0,
            latitude_deg=45.0,
            liquid_water_content_kg_m2=0.0,
        )
        assert losses.gaseous_db > 0.0
        assert losses.rain_db == 0.0
        assert losses.cloud_db == 0.0
        assert losses.total_db == pytest.approx(losses.gaseous_db)

    def test_rain_dominates_in_heavy_rain(self):
        """With heavy rain, the rain term should dominate the total."""
        losses = compute_atmospheric_losses(
            freq_ghz=30.0,
            elevation_deg=30.0,
            rain_rate_001_mm_h=80.0,
            latitude_deg=30.0,
        )
        assert losses.rain_db > losses.gaseous_db

    def test_scintillation_off_by_default(self):
        """Without include_scintillation, scintillation_db is 0."""
        losses = compute_atmospheric_losses(
            freq_ghz=1.0,
            elevation_deg=30.0,
        )
        assert losses.scintillation_db == 0.0

    def test_scintillation_included_when_requested(self):
        """With include_scintillation=True at low freq, it should be > 0."""
        losses = compute_atmospheric_losses(
            freq_ghz=0.5,
            elevation_deg=10.0,
            include_scintillation=True,
            geomagnetic_latitude_deg=10.0,
            scintillation_percentage=1.0,
        )
        assert losses.scintillation_db > 0.0

    def test_all_losses_non_negative(self):
        """Every component must be non-negative."""
        losses = compute_atmospheric_losses(
            freq_ghz=20.0,
            elevation_deg=20.0,
            rain_rate_001_mm_h=30.0,
            latitude_deg=35.0,
            liquid_water_content_kg_m2=0.5,
            include_scintillation=True,
            scintillation_percentage=1.0,
        )
        assert losses.gaseous_db >= 0.0
        assert losses.rain_db >= 0.0
        assert losses.cloud_db >= 0.0
        assert losses.scintillation_db >= 0.0
        assert losses.total_db >= 0.0
