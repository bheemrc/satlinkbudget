"""Tests for report generation."""

import pytest

from satlinkbudget.simulation._engine import PassSimulation
from satlinkbudget.simulation._report import generate_report
from satlinkbudget.orbit._propagator import Orbit
from satlinkbudget.orbit._groundstation import GroundStation
from satlinkbudget.budget._transmitter import TransmitterChain
from satlinkbudget.budget._receiver import ReceiverChain
from satlinkbudget.modem._modulation import BPSK
from satlinkbudget.modem._coding import CONV_R12_K7
from satlinkbudget.modem._performance import ModemConfig


class TestReport:
    def test_report_contains_summary(self):
        orbit = Orbit.circular(500.0, 97.4)
        gs = GroundStation("Svalbard", 78.23, 15.39, 450.0, min_elevation_deg=5.0)
        tx = TransmitterChain.from_power_dbm(33.0, 5.15)
        rx = ReceiverChain(antenna_gain_dbi=14.0, system_noise_temp_k=500.0)
        modem = ModemConfig(BPSK, CONV_R12_K7)
        sim = PassSimulation(orbit, gs, tx, rx, modem, 437e6, 9600)
        results = sim.run(duration_orbits=6, dt_s=5.0, contact_dt_s=10.0)
        report = generate_report(results)
        assert "PASS SIMULATION REPORT" in report
        assert "Total Passes" in report
        assert "Data Volume" in report
