"""Tests for patch, helix, dipole, monopole, horn antennas."""

import pytest

from satlinkbudget.antenna._patch import PatchAntenna
from satlinkbudget.antenna._helix import HelixAntenna
from satlinkbudget.antenna._dipole import DipoleAntenna, MonopoleAntenna
from satlinkbudget.antenna._horn import HornAntenna


class TestPatchAntenna:
    def test_single_element(self):
        ant = PatchAntenna(element_gain_dbi=6.0, num_elements=1)
        assert ant.gain_db() == pytest.approx(6.0, abs=0.01)

    def test_2x2_array(self):
        """4 elements → +6 dB over single element."""
        ant = PatchAntenna(element_gain_dbi=6.0, num_elements=4, rows=2, cols=2)
        assert ant.gain_db() == pytest.approx(12.0, abs=0.1)

    def test_4x4_array(self):
        """16 elements → +12 dB over single element."""
        ant = PatchAntenna(element_gain_dbi=6.0, num_elements=16, rows=4, cols=4)
        assert ant.gain_db() == pytest.approx(18.0, abs=0.1)

    def test_gain_increases_with_elements(self):
        gains = [
            PatchAntenna(6.0, n).gain_db() for n in [1, 2, 4, 8, 16]
        ]
        assert all(gains[i] < gains[i + 1] for i in range(len(gains) - 1))

    def test_beamwidth_narrows_with_rows(self):
        bw1 = PatchAntenna(6.0, 4, rows=2, cols=2).beamwidth_deg()
        bw2 = PatchAntenna(6.0, 16, rows=4, cols=4).beamwidth_deg()
        assert bw1 > bw2


class TestHelixAntenna:
    def test_typical_uhf_helix(self):
        """10-turn UHF helix ≈ 12-14 dBi."""
        ant = HelixAntenna(
            num_turns=10,
            circumference_m=0.687,  # ~λ at 437 MHz
            spacing_m=0.172,  # ~λ/4
        )
        gain = ant.gain_db(437e6)
        assert 11.0 < gain < 16.0

    def test_gain_increases_with_turns(self):
        gains = [
            HelixAntenna(n, 0.687, 0.172).gain_db(437e6)
            for n in [5, 10, 15, 20]
        ]
        assert all(gains[i] < gains[i + 1] for i in range(len(gains) - 1))

    def test_beamwidth_positive(self):
        ant = HelixAntenna(10, 0.687, 0.172)
        assert ant.beamwidth_deg(437e6) > 0


class TestDipoleAntenna:
    def test_gain(self):
        ant = DipoleAntenna()
        assert ant.gain_db() == pytest.approx(2.15)

    def test_gain_frequency_independent(self):
        ant = DipoleAntenna()
        assert ant.gain_db(100e6) == ant.gain_db(1e9)

    def test_beamwidth(self):
        assert DipoleAntenna().beamwidth_deg() == pytest.approx(78.0)


class TestMonopoleAntenna:
    def test_gain(self):
        ant = MonopoleAntenna()
        assert ant.gain_db() == pytest.approx(5.15)

    def test_higher_than_dipole(self):
        assert MonopoleAntenna().gain_db() > DipoleAntenna().gain_db()


class TestHornAntenna:
    def test_typical_horn(self):
        """X-band horn ≈ 15-25 dBi."""
        ant = HornAntenna(width_m=0.1, height_m=0.08, efficiency=0.51)
        gain = ant.gain_db(8.2e9)
        assert 15.0 < gain < 25.0

    def test_gain_increases_with_aperture(self):
        g1 = HornAntenna(0.05, 0.04).gain_db(10e9)
        g2 = HornAntenna(0.1, 0.08).gain_db(10e9)
        assert g2 > g1

    def test_gain_increases_with_frequency(self):
        ant = HornAntenna(0.1, 0.08)
        g1 = ant.gain_db(4e9)
        g2 = ant.gain_db(8e9)
        assert g2 > g1

    def test_beamwidth_positive(self):
        ant = HornAntenna(0.1, 0.08)
        assert ant.beamwidth_deg(8e9) > 0
