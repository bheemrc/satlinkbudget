"""Tests for noise temperature and G/T calculations."""

import numpy as np
import pytest

from satlinkbudget.rf._noise import (
    antenna_noise_temperature,
    figure_of_merit_db,
    noise_figure_to_temperature,
    rain_noise_temperature,
    system_noise_temperature,
)


class TestSystemNoiseTemperature:
    def test_basic_friis(self):
        """T_sys = T_ant + T_lna when no subsequent stages."""
        t_sys = system_noise_temperature(50.0, 75.0, 30.0)
        assert t_sys == pytest.approx(125.0, abs=0.1)

    def test_with_subsequent(self):
        """Subsequent stage contribution divided by LNA gain."""
        # G_lna = 30 dB = 1000x, subsequent = 1000 K → adds 1 K
        t_sys = system_noise_temperature(50.0, 75.0, 30.0, 1000.0)
        assert t_sys == pytest.approx(126.0, abs=0.1)

    def test_high_gain_suppresses_subsequent(self):
        """High LNA gain makes subsequent stages negligible."""
        t_low = system_noise_temperature(50.0, 75.0, 40.0, 5000.0)
        t_no_sub = system_noise_temperature(50.0, 75.0, 40.0, 0.0)
        assert abs(t_low - t_no_sub) < 1.0

    def test_zero_gain(self):
        """0 dB gain means subsequent adds directly."""
        t_sys = system_noise_temperature(50.0, 75.0, 0.0, 100.0)
        assert t_sys == pytest.approx(225.0, abs=0.1)

    def test_always_positive(self):
        """System noise temperature is always positive."""
        t_sys = system_noise_temperature(3.0, 10.0, 30.0, 100.0)
        assert t_sys > 0


class TestNoiseFigureToTemperature:
    def test_0db_nf(self):
        """0 dB NF → 0 K noise temperature."""
        assert noise_figure_to_temperature(0.0) == pytest.approx(0.0, abs=0.01)

    def test_1db_nf(self):
        """1 dB NF → ~75 K."""
        t = noise_figure_to_temperature(1.0)
        assert t == pytest.approx(75.1, abs=1.0)

    def test_3db_nf(self):
        """3 dB NF → ~289 K (exact 290 K at 3.0103 dB)."""
        t = noise_figure_to_temperature(3.0)
        assert t == pytest.approx(288.6, abs=1.0)

    def test_increases_with_nf(self):
        """Higher NF → higher noise temperature."""
        temps = [noise_figure_to_temperature(nf) for nf in [0.5, 1.0, 2.0, 3.0, 6.0]]
        assert all(temps[i] < temps[i + 1] for i in range(len(temps) - 1))


class TestFigureOfMerit:
    def test_known_value(self):
        """G = 40 dBi, T = 100 K → G/T = 40 - 20 = 20 dB/K."""
        got = figure_of_merit_db(40.0, 100.0)
        assert got == pytest.approx(20.0, abs=0.01)

    def test_high_gain_low_temp(self):
        """DSN 70m at X-band: G ≈ 74 dBi, T ≈ 20 K → G/T ≈ 61 dB/K."""
        got = figure_of_merit_db(74.0, 20.0)
        assert got == pytest.approx(60.99, abs=0.1)

    def test_increases_with_gain(self):
        """Higher gain improves G/T."""
        gt1 = figure_of_merit_db(30.0, 200.0)
        gt2 = figure_of_merit_db(40.0, 200.0)
        assert gt2 > gt1

    def test_decreases_with_temperature(self):
        """Higher noise temperature degrades G/T."""
        gt1 = figure_of_merit_db(40.0, 100.0)
        gt2 = figure_of_merit_db(40.0, 200.0)
        assert gt1 > gt2


class TestAntennaNoise:
    def test_low_freq_high(self):
        """VHF has high galactic noise."""
        t = antenna_noise_temperature(150e6, 45.0)
        assert t > 100.0

    def test_s_band_moderate(self):
        """S-band (2.2 GHz) has moderate sky noise."""
        t = antenna_noise_temperature(2.2e9, 45.0)
        assert 5.0 < t < 100.0

    def test_x_band_low(self):
        """X-band (8 GHz) sky noise is low."""
        t = antenna_noise_temperature(8.2e9, 45.0)
        assert 3.0 < t < 50.0

    def test_elevation_effect(self):
        """Lower elevation → more ground noise."""
        t_low = antenna_noise_temperature(2e9, 10.0)
        t_high = antenna_noise_temperature(2e9, 80.0)
        assert t_low > t_high

    def test_always_positive(self):
        """Antenna noise temperature is always positive."""
        for freq in [150e6, 437e6, 2.2e9, 8.2e9, 26e9]:
            for el in [5, 30, 60, 90]:
                assert antenna_noise_temperature(freq, el) > 0


class TestRainNoise:
    def test_zero_rain(self):
        """No rain attenuation → no additional noise."""
        assert rain_noise_temperature(0.0) == pytest.approx(0.0, abs=0.01)

    def test_heavy_rain(self):
        """Heavy rain (10 dB) approaches medium temperature."""
        t = rain_noise_temperature(10.0, 275.0)
        assert t == pytest.approx(275.0 * (1.0 - 0.1), abs=1.0)

    def test_moderate_rain(self):
        """3 dB rain → about half the medium temperature."""
        t = rain_noise_temperature(3.0, 275.0)
        assert t == pytest.approx(275.0 * 0.5, abs=1.0)

    def test_increases_with_attenuation(self):
        """More rain attenuation → more noise."""
        temps = [rain_noise_temperature(a) for a in [0.5, 1.0, 3.0, 5.0, 10.0]]
        assert all(temps[i] < temps[i + 1] for i in range(len(temps) - 1))

    def test_bounded(self):
        """Rain noise never exceeds medium temperature."""
        for a in [0.1, 1.0, 5.0, 20.0, 100.0]:
            assert 0 <= rain_noise_temperature(a, 275.0) <= 275.0
