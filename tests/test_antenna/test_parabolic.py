"""Tests for parabolic dish antenna."""

import pytest

from satlinkbudget.antenna._parabolic import ParabolicAntenna


class TestParabolicAntenna:
    def test_gain_3_7m_x_band(self):
        """3.7m dish at 8.2 GHz: G = 0.55·(π·3.7·8.2e9/c)² ≈ 47.5 dBi."""
        ant = ParabolicAntenna(diameter_m=3.7, efficiency=0.55)
        gain = ant.gain_db(8.2e9)
        assert gain == pytest.approx(47.45, abs=0.5)

    def test_gain_2_4m_s_band(self):
        """2.4m dish at 2.2 GHz ≈ 32.3 dBi."""
        ant = ParabolicAntenna(diameter_m=2.4, efficiency=0.55)
        gain = ant.gain_db(2.2e9)
        assert gain == pytest.approx(32.3, abs=0.5)

    def test_gain_increases_with_diameter(self):
        for freq in [2.2e9, 8.2e9]:
            gains = [
                ParabolicAntenna(d).gain_db(freq) for d in [1.0, 2.0, 4.0, 8.0]
            ]
            assert all(gains[i] < gains[i + 1] for i in range(len(gains) - 1))

    def test_gain_increases_with_frequency(self):
        ant = ParabolicAntenna(diameter_m=3.7)
        gains = [ant.gain_db(f) for f in [1e9, 2e9, 4e9, 8e9]]
        assert all(gains[i] < gains[i + 1] for i in range(len(gains) - 1))

    def test_double_diameter_6db(self):
        """Doubling diameter adds ~6 dB gain."""
        g1 = ParabolicAntenna(2.0).gain_db(8e9)
        g2 = ParabolicAntenna(4.0).gain_db(8e9)
        assert (g2 - g1) == pytest.approx(6.02, abs=0.1)

    def test_beamwidth_decreases_with_size(self):
        bw1 = ParabolicAntenna(2.0).beamwidth_deg(8e9)
        bw2 = ParabolicAntenna(4.0).beamwidth_deg(8e9)
        assert bw1 > bw2

    def test_beamwidth_positive(self):
        ant = ParabolicAntenna(diameter_m=3.7)
        assert ant.beamwidth_deg(8.2e9) > 0

    def test_efficiency_effect(self):
        """Higher efficiency → higher gain."""
        g1 = ParabolicAntenna(3.7, efficiency=0.4).gain_db(8e9)
        g2 = ParabolicAntenna(3.7, efficiency=0.7).gain_db(8e9)
        assert g2 > g1
