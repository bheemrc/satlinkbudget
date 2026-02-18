"""End-to-end integration tests."""

import subprocess
import sys
from pathlib import Path

import pytest

from satlinkbudget.api._services import run_link_budget, run_pass_simulation
from satlinkbudget.api._schemas import LinkBudgetRequest, PassSimulationRequest
from satlinkbudget.rf._path_loss import slant_range


MISSIONS_DIR = Path(__file__).parent.parent.parent / "src" / "satlinkbudget" / "data" / "missions"


class TestEndToEnd:
    def test_uhf_cubesat_link_budget(self):
        """Reproduce a known UHF CubeSat link budget."""
        req = LinkBudgetRequest(
            tx_power_dbm=33.0,
            tx_antenna_gain_dbi=5.15,
            tx_pointing_loss_db=1.0,
            rx_antenna_gain_dbi=14.0,
            rx_system_noise_temp_k=500.0,
            rx_feed_loss_db=0.5,
            frequency_hz=437e6,
            distance_m=slant_range(500e3, 30.0),
            data_rate_bps=9600,
            modulation="BPSK",
            coding="convolutional_r12",
            atmospheric_loss_db=0.5,
        )
        resp = run_link_budget(req)
        assert resp.summary.link_closes
        assert resp.summary.margin_db > 5.0

    def test_api_import(self):
        """API layer is importable."""
        from satlinkbudget.api import run_link_budget as rlb
        assert callable(rlb)

    def test_cli_list(self):
        """CLI list subcommand works."""
        result = subprocess.run(
            [sys.executable, "-m", "satlinkbudget", "list", "transceivers"],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0
        assert "endurosat" in result.stdout.lower()

    def test_cli_budget(self):
        """CLI budget subcommand works."""
        mission_path = MISSIONS_DIR / "cubesat_uhf_downlink.yaml"
        result = subprocess.run(
            [sys.executable, "-m", "satlinkbudget", "budget", str(mission_path), "--elevation", "30"],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0
        assert "MARGIN" in result.stdout

    def test_preset_simulation_api(self):
        """API simulation with preset works."""
        req = PassSimulationRequest(
            mission_preset="cubesat_uhf_downlink",
            duration_orbits=3,
            dt_s=5.0,
        )
        resp = run_pass_simulation(req)
        assert resp.summary.num_passes >= 0
        assert "REPORT" in resp.text_report
