"""Tests for mission config and builder."""

from pathlib import Path

import pytest

from satlinkbudget.mission._config import LinkMissionConfig
from satlinkbudget.mission._builder import load_mission, build_pass_simulation
from satlinkbudget.data._registry import registry


MISSIONS_DIR = Path(__file__).parent.parent.parent / "src" / "satlinkbudget" / "data" / "missions"


class TestMissionConfig:
    def test_load_cubesat_uhf(self):
        config = load_mission(MISSIONS_DIR / "cubesat_uhf_downlink.yaml")
        assert config.name == "CubeSat UHF Downlink"
        assert config.frequency_hz == pytest.approx(437e6)
        assert config.orbit.altitude_km == 500

    def test_load_all_presets(self):
        """All preset YAMLs should parse without error."""
        for name in registry.list_missions():
            path = MISSIONS_DIR / f"{name}.yaml"
            config = load_mission(path)
            assert config.name != ""
            assert config.frequency_hz > 0

    def test_build_cubesat_uhf(self):
        config = load_mission(MISSIONS_DIR / "cubesat_uhf_downlink.yaml")
        sim = build_pass_simulation(config)
        assert sim.frequency_hz == pytest.approx(437e6)
        assert sim.data_rate_bps == pytest.approx(9600)

    def test_build_and_run_cubesat_uhf(self):
        config = load_mission(MISSIONS_DIR / "cubesat_uhf_downlink.yaml")
        sim = build_pass_simulation(config)
        results = sim.run(duration_orbits=6, dt_s=5.0, contact_dt_s=10.0)
        assert results.num_passes >= 0

    def test_build_s_band(self):
        config = load_mission(MISSIONS_DIR / "cubesat_s_band_downlink.yaml")
        sim = build_pass_simulation(config)
        assert sim.frequency_hz == pytest.approx(2.2e9)

    def test_build_x_band(self):
        config = load_mission(MISSIONS_DIR / "eo_x_band_downlink.yaml")
        sim = build_pass_simulation(config)
        assert sim.frequency_hz == pytest.approx(8.2e9)

    def test_build_iot(self):
        config = load_mission(MISSIONS_DIR / "iot_uhf_uplink.yaml")
        sim = build_pass_simulation(config)
        assert sim.data_rate_bps == pytest.approx(1200)

    def test_build_deep_space(self):
        config = load_mission(MISSIONS_DIR / "deep_space_x_band.yaml")
        sim = build_pass_simulation(config)
        assert sim.frequency_hz == pytest.approx(8.4e9)
