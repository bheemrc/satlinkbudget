"""Tests for transmitter chain."""

import pytest

from satlinkbudget.budget._transmitter import TransmitterChain


class TestTransmitterChain:
    def test_basic_eirp(self):
        """1W (0 dBW) + 10 dBi = 10 dBW EIRP."""
        tx = TransmitterChain(power_dbw=0.0, antenna_gain_dbi=10.0)
        assert tx.eirp_dbw == pytest.approx(10.0)

    def test_eirp_with_losses(self):
        """EIRP accounts for feed and pointing losses."""
        tx = TransmitterChain(
            power_dbw=3.0,
            antenna_gain_dbi=5.0,
            feed_loss_db=1.0,
            pointing_loss_db=0.5,
        )
        assert tx.eirp_dbw == pytest.approx(6.5)

    def test_from_power_dbm(self):
        """33 dBm = 3 dBW."""
        tx = TransmitterChain.from_power_dbm(33.0, 5.15)
        assert tx.power_dbw == pytest.approx(3.0)
        assert tx.eirp_dbw == pytest.approx(8.15)

    def test_cubesat_uhf(self):
        """Typical CubeSat UHF: 33 dBm + 5 dBi monopole."""
        tx = TransmitterChain.from_power_dbm(
            33.0, 5.15, feed_loss_db=0.5, pointing_loss_db=1.0
        )
        assert 5.0 < tx.eirp_dbw < 10.0

    def test_other_loss(self):
        tx = TransmitterChain(
            power_dbw=0.0, antenna_gain_dbi=10.0, other_loss_db=2.0
        )
        assert tx.eirp_dbw == pytest.approx(8.0)
