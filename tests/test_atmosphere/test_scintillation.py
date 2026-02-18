"""Tests for ITU-R P.531 ionospheric scintillation model."""

import pytest

from satlinkbudget.atmosphere._scintillation import (
    ionospheric_scintillation_loss,
    scintillation_index_s4,
)


class TestScintillationIndexS4:
    def test_decreases_with_frequency(self):
        """S4 decreases strongly with frequency (~ f^{-1.5})."""
        s4_vhf = scintillation_index_s4(0.3)   # 300 MHz
        s4_uhf = scintillation_index_s4(1.0)   # 1 GHz
        s4_l = scintillation_index_s4(1.5)     # L-band
        s4_x = scintillation_index_s4(8.0)     # X-band
        assert s4_vhf > s4_uhf > s4_l > s4_x

    def test_negligible_above_4ghz(self):
        """Above ~4 GHz, S4 is very small at mid-latitudes."""
        s4 = scintillation_index_s4(4.0, geomagnetic_latitude_deg=45.0)
        assert s4 < 0.1

    def test_significant_at_vhf(self):
        """At VHF (300 MHz), S4 can be quite large."""
        s4 = scintillation_index_s4(0.3, geomagnetic_latitude_deg=10.0)
        assert s4 > 0.5

    def test_equatorial_stronger_than_midlat(self):
        """Equatorial region has stronger scintillation than mid-latitude."""
        s4_eq = scintillation_index_s4(1.0, geomagnetic_latitude_deg=5.0)
        s4_mid = scintillation_index_s4(1.0, geomagnetic_latitude_deg=45.0)
        assert s4_eq > s4_mid

    def test_higher_solar_activity_stronger(self):
        """Higher solar flux index → stronger scintillation."""
        s4_low = scintillation_index_s4(1.0, solar_flux_index=70.0)
        s4_high = scintillation_index_s4(1.0, solar_flux_index=200.0)
        assert s4_high > s4_low

    def test_nighttime_stronger_than_daytime(self):
        """Post-sunset scintillation is stronger than daytime."""
        s4_night = scintillation_index_s4(1.0, local_time_hours=21.0)
        s4_day = scintillation_index_s4(1.0, local_time_hours=12.0)
        assert s4_night > s4_day

    def test_always_non_negative(self):
        """S4 is always non-negative."""
        for f in [0.1, 0.5, 1.0, 5.0, 20.0]:
            assert scintillation_index_s4(f) >= 0.0

    def test_raises_on_negative_freq(self):
        """Negative frequency raises ValueError."""
        with pytest.raises(ValueError, match="freq_ghz must be positive"):
            scintillation_index_s4(-1.0)


class TestIonosphericScintillationLoss:
    def test_positive_at_low_frequency(self):
        """At UHF, scintillation loss should be positive."""
        loss = ionospheric_scintillation_loss(0.5, 30.0)
        assert loss > 0.0

    def test_negligible_at_high_frequency(self):
        """At X-band and above, scintillation loss should be tiny."""
        loss = ionospheric_scintillation_loss(
            10.0, 30.0, geomagnetic_latitude_deg=45.0
        )
        assert loss < 0.5

    def test_lower_elevation_more_loss(self):
        """Lower elevation → more oblique path → more scintillation."""
        loss_low = ionospheric_scintillation_loss(1.0, 10.0)
        loss_high = ionospheric_scintillation_loss(1.0, 60.0)
        assert loss_low > loss_high

    def test_elevation_clamped_at_5deg(self):
        """Very low elevations should be clamped."""
        loss_1 = ionospheric_scintillation_loss(1.0, 1.0)
        loss_5 = ionospheric_scintillation_loss(1.0, 5.0)
        assert loss_1 == pytest.approx(loss_5, rel=1e-10)

    def test_decreases_with_frequency(self):
        """Higher frequency → less scintillation loss."""
        loss_vhf = ionospheric_scintillation_loss(0.3, 30.0)
        loss_uhf = ionospheric_scintillation_loss(1.0, 30.0)
        loss_sband = ionospheric_scintillation_loss(2.0, 30.0)
        assert loss_vhf > loss_uhf > loss_sband

    def test_raises_on_bad_percentage(self):
        """Invalid percentage raises ValueError."""
        with pytest.raises(ValueError, match="percentage"):
            ionospheric_scintillation_loss(1.0, 30.0, percentage=0.0)
        with pytest.raises(ValueError, match="percentage"):
            ionospheric_scintillation_loss(1.0, 30.0, percentage=100.0)
