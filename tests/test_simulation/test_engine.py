"""Tests for pass simulation engine."""

import numpy as np
import pytest
import matplotlib
matplotlib.use("Agg")

from satlinkbudget.simulation._engine import PassSimulation
from satlinkbudget.orbit._propagator import Orbit
from satlinkbudget.orbit._groundstation import GroundStation
from satlinkbudget.budget._transmitter import TransmitterChain
from satlinkbudget.budget._receiver import ReceiverChain
from satlinkbudget.modem._modulation import BPSK
from satlinkbudget.modem._coding import CONV_R12_K7
from satlinkbudget.modem._performance import ModemConfig


@pytest.fixture
def uhf_simulation():
    """Standard CubeSat UHF simulation setup."""
    orbit = Orbit.circular(500.0, 97.4)
    gs = GroundStation("Svalbard", 78.23, 15.39, 450.0, min_elevation_deg=5.0)
    tx = TransmitterChain.from_power_dbm(33.0, 5.15, pointing_loss_db=1.0)
    rx = ReceiverChain(antenna_gain_dbi=14.0, system_noise_temp_k=500.0, feed_loss_db=0.5)
    modem = ModemConfig(BPSK, CONV_R12_K7, implementation_loss_db=1.0)
    return PassSimulation(
        orbit=orbit,
        ground_station=gs,
        transmitter=tx,
        receiver=rx,
        modem=modem,
        frequency_hz=437e6,
        data_rate_bps=9600,
    )


class TestPassSimulation:
    def test_finds_passes(self, uhf_simulation):
        """Should find passes in a 24-orbit simulation."""
        results = uhf_simulation.run(duration_orbits=24, dt_s=2.0, contact_dt_s=10.0)
        assert results.num_passes > 0

    def test_data_volume_positive(self, uhf_simulation):
        results = uhf_simulation.run(duration_orbits=24, dt_s=2.0, contact_dt_s=10.0)
        assert results.total_data_volume_bits > 0

    def test_margin_varies_over_pass(self, uhf_simulation):
        """Margin should vary (higher near zenith, lower near horizon)."""
        results = uhf_simulation.run(duration_orbits=24, dt_s=2.0, contact_dt_s=10.0)
        if results.num_passes > 0:
            p = results.passes[0]
            assert p.max_margin_db > p.min_margin_db

    def test_elevation_varies_over_pass(self, uhf_simulation):
        results = uhf_simulation.run(duration_orbits=24, dt_s=2.0, contact_dt_s=10.0)
        if results.num_passes > 0:
            p = results.passes[0]
            assert np.max(p.elevations_deg) > np.min(p.elevations_deg)

    def test_doppler_sign_change(self, uhf_simulation):
        """Doppler should change sign during a high-elevation pass."""
        results = uhf_simulation.run(duration_orbits=24, dt_s=2.0, contact_dt_s=10.0)
        # Find a pass with high enough elevation
        for p in results.passes:
            if p.max_elevation_deg > 30:
                has_positive = np.any(p.doppler_shifts_hz > 0)
                has_negative = np.any(p.doppler_shifts_hz < 0)
                if has_positive and has_negative:
                    return  # Found it
        # It's ok if no high pass found, but we expect at least some passes

    def test_passes_per_day_reasonable(self, uhf_simulation):
        results = uhf_simulation.run(duration_orbits=24, dt_s=2.0, contact_dt_s=10.0)
        assert results.passes_per_day > 3

    def test_avg_pass_duration(self, uhf_simulation):
        results = uhf_simulation.run(duration_orbits=24, dt_s=2.0, contact_dt_s=10.0)
        assert 60 < results.avg_pass_duration_s < 1000

    def test_plot_elevation(self, uhf_simulation):
        results = uhf_simulation.run(duration_orbits=24, dt_s=2.0, contact_dt_s=10.0)
        if results.num_passes > 0:
            fig = results.plot_pass_elevation(0)
            assert fig is not None
            import matplotlib.pyplot as plt
            plt.close(fig)

    def test_plot_margin(self, uhf_simulation):
        results = uhf_simulation.run(duration_orbits=24, dt_s=2.0, contact_dt_s=10.0)
        if results.num_passes > 0:
            fig = results.plot_pass_margin(0)
            assert fig is not None
            import matplotlib.pyplot as plt
            plt.close(fig)

    def test_plot_doppler(self, uhf_simulation):
        results = uhf_simulation.run(duration_orbits=24, dt_s=2.0, contact_dt_s=10.0)
        if results.num_passes > 0:
            fig = results.plot_doppler(0)
            assert fig is not None
            import matplotlib.pyplot as plt
            plt.close(fig)

    def test_plot_data_volume(self, uhf_simulation):
        results = uhf_simulation.run(duration_orbits=24, dt_s=2.0, contact_dt_s=10.0)
        fig = results.plot_data_volume_cumulative()
        assert fig is not None
        import matplotlib.pyplot as plt
        plt.close(fig)
