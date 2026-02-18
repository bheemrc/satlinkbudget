"""Tests for link budget computation."""

import numpy as np
import pytest

from satlinkbudget.budget._transmitter import TransmitterChain
from satlinkbudget.budget._receiver import ReceiverChain
from satlinkbudget.budget._link import (
    compute_link_budget,
    compute_max_data_rate,
    compute_required_power_dbw,
)
from satlinkbudget.rf._path_loss import slant_range


class TestComputeLinkBudget:
    @pytest.fixture
    def cubesat_uhf_budget(self):
        """Typical CubeSat UHF downlink at 500km, 30° elevation."""
        tx = TransmitterChain.from_power_dbm(33.0, 5.15, pointing_loss_db=1.0)
        rx = ReceiverChain(
            antenna_gain_dbi=14.0, system_noise_temp_k=500.0, feed_loss_db=0.5
        )
        dist = slant_range(500e3, 30.0)
        return compute_link_budget(
            transmitter=tx,
            receiver=rx,
            frequency_hz=437e6,
            distance_m=dist,
            data_rate_bps=9600,
            required_eb_n0_db=9.6,
            atmospheric_loss_db=0.5,
        )

    def test_cubesat_uhf_closes(self, cubesat_uhf_budget):
        """Typical UHF CubeSat budget should close."""
        assert cubesat_uhf_budget.link_closes

    def test_cubesat_uhf_margin_range(self, cubesat_uhf_budget):
        """UHF CubeSat margin positive and reasonable."""
        assert 3.0 < cubesat_uhf_budget.margin_db < 40.0

    def test_margin_decreases_with_distance(self):
        """More distance → more FSPL → less margin."""
        tx = TransmitterChain(power_dbw=3.0, antenna_gain_dbi=5.0)
        rx = ReceiverChain(antenna_gain_dbi=14.0, system_noise_temp_k=500.0)
        m1 = compute_link_budget(tx, rx, 437e6, 500e3, 9600, 9.6).margin_db
        m2 = compute_link_budget(tx, rx, 437e6, 2000e3, 9600, 9.6).margin_db
        assert m1 > m2

    def test_margin_increases_with_power(self):
        """More TX power → better margin."""
        rx = ReceiverChain(antenna_gain_dbi=14.0, system_noise_temp_k=500.0)
        tx1 = TransmitterChain(power_dbw=0.0, antenna_gain_dbi=5.0)
        tx2 = TransmitterChain(power_dbw=3.0, antenna_gain_dbi=5.0)
        m1 = compute_link_budget(tx1, rx, 437e6, 1000e3, 9600, 9.6).margin_db
        m2 = compute_link_budget(tx2, rx, 437e6, 1000e3, 9600, 9.6).margin_db
        assert m2 > m1
        assert (m2 - m1) == pytest.approx(3.0, abs=0.01)

    def test_higher_data_rate_less_margin(self):
        """Doubling data rate costs 3 dB margin."""
        tx = TransmitterChain(power_dbw=3.0, antenna_gain_dbi=5.0)
        rx = ReceiverChain(antenna_gain_dbi=14.0, system_noise_temp_k=500.0)
        m1 = compute_link_budget(tx, rx, 437e6, 1000e3, 9600, 9.6).margin_db
        m2 = compute_link_budget(tx, rx, 437e6, 1000e3, 19200, 9.6).margin_db
        assert (m1 - m2) == pytest.approx(3.01, abs=0.1)

    def test_eirp_decomposition(self, cubesat_uhf_budget):
        """EIRP = P + G - losses."""
        r = cubesat_uhf_budget
        expected = (
            r.tx_power_dbw
            + r.tx_antenna_gain_dbi
            - r.tx_feed_loss_db
            - r.tx_pointing_loss_db
            - r.tx_other_loss_db
        )
        assert r.eirp_dbw == pytest.approx(expected)

    def test_to_text_contains_key_fields(self, cubesat_uhf_budget):
        text = cubesat_uhf_budget.to_text()
        assert "EIRP" in text
        assert "MARGIN" in text
        assert "C/N" in text

    def test_summary_dict(self, cubesat_uhf_budget):
        s = cubesat_uhf_budget.summary()
        assert "margin_db" in s
        assert "eirp_dbw" in s


class TestComputeMaxDataRate:
    def test_positive_rate(self):
        """Closing link should have positive max data rate."""
        tx = TransmitterChain(power_dbw=3.0, antenna_gain_dbi=5.0)
        rx = ReceiverChain(antenna_gain_dbi=14.0, system_noise_temp_k=500.0)
        rate = compute_max_data_rate(
            tx, rx, 437e6, 1000e3, required_eb_n0_db=9.6, target_margin_db=3.0
        )
        assert rate > 0

    def test_increases_with_power(self):
        """More power → higher max data rate."""
        rx = ReceiverChain(antenna_gain_dbi=14.0, system_noise_temp_k=500.0)
        tx1 = TransmitterChain(power_dbw=0.0, antenna_gain_dbi=5.0)
        tx2 = TransmitterChain(power_dbw=10.0, antenna_gain_dbi=5.0)
        r1 = compute_max_data_rate(tx1, rx, 437e6, 1000e3, 9.6)
        r2 = compute_max_data_rate(tx2, rx, 437e6, 1000e3, 9.6)
        assert r2 > r1


class TestInputValidation:
    def test_link_budget_rejects_negative_frequency(self):
        tx = TransmitterChain(power_dbw=3.0, antenna_gain_dbi=5.0)
        rx = ReceiverChain(antenna_gain_dbi=14.0, system_noise_temp_k=500.0)
        with pytest.raises(ValueError, match="frequency"):
            compute_link_budget(tx, rx, -1.0, 1000e3, 9600, 9.6)

    def test_link_budget_rejects_zero_distance(self):
        tx = TransmitterChain(power_dbw=3.0, antenna_gain_dbi=5.0)
        rx = ReceiverChain(antenna_gain_dbi=14.0, system_noise_temp_k=500.0)
        with pytest.raises(ValueError, match="distance"):
            compute_link_budget(tx, rx, 437e6, 0.0, 9600, 9.6)

    def test_link_budget_rejects_zero_data_rate(self):
        tx = TransmitterChain(power_dbw=3.0, antenna_gain_dbi=5.0)
        rx = ReceiverChain(antenna_gain_dbi=14.0, system_noise_temp_k=500.0)
        with pytest.raises(ValueError, match="data_rate"):
            compute_link_budget(tx, rx, 437e6, 1000e3, 0.0, 9.6)

    def test_max_data_rate_rejects_negative_frequency(self):
        tx = TransmitterChain(power_dbw=3.0, antenna_gain_dbi=5.0)
        rx = ReceiverChain(antenna_gain_dbi=14.0, system_noise_temp_k=500.0)
        with pytest.raises(ValueError, match="frequency"):
            compute_max_data_rate(tx, rx, -1.0, 1000e3, 9.6)

    def test_required_power_rejects_negative_frequency(self):
        rx = ReceiverChain(antenna_gain_dbi=14.0, system_noise_temp_k=500.0)
        with pytest.raises(ValueError, match="frequency"):
            compute_required_power_dbw(rx, -1.0, 1000e3, 9600, 9.6)

    def test_required_power_rejects_zero_distance(self):
        rx = ReceiverChain(antenna_gain_dbi=14.0, system_noise_temp_k=500.0)
        with pytest.raises(ValueError, match="distance"):
            compute_required_power_dbw(rx, 437e6, 0.0, 9600, 9.6)

    def test_required_power_rejects_zero_data_rate(self):
        rx = ReceiverChain(antenna_gain_dbi=14.0, system_noise_temp_k=500.0)
        with pytest.raises(ValueError, match="data_rate"):
            compute_required_power_dbw(rx, 437e6, 1000e3, 0.0, 9.6)


class TestComputeRequiredPower:
    def test_reasonable_power(self):
        """Required power should be in reasonable range for CubeSat."""
        rx = ReceiverChain(antenna_gain_dbi=14.0, system_noise_temp_k=500.0)
        p = compute_required_power_dbw(
            rx,
            437e6,
            1000e3,
            9600,
            required_eb_n0_db=9.6,
            target_margin_db=3.0,
            tx_antenna_gain_dbi=5.0,
        )
        # UHF at 9600 bps with 14 dBi ground antenna needs very little power
        assert -30.0 < p < 20.0

    def test_more_margin_more_power(self):
        """Higher target margin requires more power."""
        rx = ReceiverChain(antenna_gain_dbi=14.0, system_noise_temp_k=500.0)
        p1 = compute_required_power_dbw(
            rx, 437e6, 1000e3, 9600, 9.6, target_margin_db=3.0, tx_antenna_gain_dbi=5.0
        )
        p2 = compute_required_power_dbw(
            rx, 437e6, 1000e3, 9600, 9.6, target_margin_db=6.0, tx_antenna_gain_dbi=5.0
        )
        assert p2 > p1
        assert (p2 - p1) == pytest.approx(3.0, abs=0.01)
