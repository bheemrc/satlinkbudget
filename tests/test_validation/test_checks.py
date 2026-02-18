"""Tests for validation checks."""

import pytest

from satlinkbudget.validation._checks import (
    validate_frequency_band,
    validate_eirp_limit,
    validate_link_closes,
    validate_antenna_gain,
    validate_data_rate,
)
from satlinkbudget.budget._transmitter import TransmitterChain
from satlinkbudget.budget._receiver import ReceiverChain


class TestValidation:
    def test_frequency_in_band(self):
        r = validate_frequency_band(437e6, 435e6, 438e6)
        assert r.valid

    def test_frequency_out_of_band(self):
        r = validate_frequency_band(500e6, 435e6, 438e6)
        assert not r.valid

    def test_eirp_within_limit(self):
        r = validate_eirp_limit(5.0, 10.0)
        assert r.valid

    def test_eirp_exceeds_limit(self):
        r = validate_eirp_limit(15.0, 10.0)
        assert not r.valid

    def test_link_closes_at_30deg(self):
        tx = TransmitterChain.from_power_dbm(33.0, 5.15)
        rx = ReceiverChain(antenna_gain_dbi=14.0, system_noise_temp_k=500.0)
        r = validate_link_closes(tx, rx, 437e6, 500e3, 9600, 9.6, min_elevation_deg=30.0)
        assert r.valid

    def test_antenna_gain_reasonable(self):
        r = validate_antenna_gain(40.0, 8.2e9)
        assert r.valid

    def test_antenna_gain_too_high(self):
        r = validate_antenna_gain(100.0, 1e9)
        assert not r.valid

    def test_data_rate_achievable(self):
        r = validate_data_rate(9600, 25000, 1.0)
        assert r.valid

    def test_data_rate_too_high(self):
        r = validate_data_rate(100000, 25000, 1.0)
        assert not r.valid
