"""Tests for receiver chain."""

import numpy as np
import pytest

from satlinkbudget.budget._receiver import ReceiverChain


class TestReceiverChain:
    def test_basic_g_over_t(self):
        """40 dBi, 100 K → G/T = 20 dB/K."""
        rx = ReceiverChain(antenna_gain_dbi=40.0, system_noise_temp_k=100.0)
        assert rx.figure_of_merit_db_per_k == pytest.approx(20.0, abs=0.01)

    def test_with_losses(self):
        """Losses reduce effective G/T."""
        rx = ReceiverChain(
            antenna_gain_dbi=40.0,
            system_noise_temp_k=100.0,
            feed_loss_db=1.0,
            pointing_loss_db=0.5,
        )
        assert rx.figure_of_merit_db_per_k == pytest.approx(18.5, abs=0.01)

    def test_dsn_station(self):
        """DSN 34m: G ≈ 68 dBi, T ≈ 25 K → G/T ≈ 54 dB/K."""
        rx = ReceiverChain(antenna_gain_dbi=68.0, system_noise_temp_k=25.0)
        got = rx.figure_of_merit_db_per_k
        expected = 68.0 - 10.0 * np.log10(25.0)
        assert got == pytest.approx(expected, abs=0.01)

    def test_higher_temp_worse(self):
        """Higher noise temperature → lower G/T."""
        rx1 = ReceiverChain(antenna_gain_dbi=40.0, system_noise_temp_k=100.0)
        rx2 = ReceiverChain(antenna_gain_dbi=40.0, system_noise_temp_k=500.0)
        assert rx1.figure_of_merit_db_per_k > rx2.figure_of_merit_db_per_k

    def test_higher_gain_better(self):
        """Higher antenna gain → higher G/T."""
        rx1 = ReceiverChain(antenna_gain_dbi=30.0, system_noise_temp_k=100.0)
        rx2 = ReceiverChain(antenna_gain_dbi=40.0, system_noise_temp_k=100.0)
        assert rx2.figure_of_merit_db_per_k > rx1.figure_of_merit_db_per_k
