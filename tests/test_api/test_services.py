"""Tests for API services."""

import pytest

from satlinkbudget.api._schemas import LinkBudgetRequest, PassSimulationRequest
from satlinkbudget.api._services import (
    run_link_budget,
    run_pass_simulation,
    list_components,
    get_component,
    get_presets,
)
from satlinkbudget.api._errors import ConfigurationError, ComponentNotFoundError
from satlinkbudget.api._serializers import NumpyEncoder, serialize_results
from satlinkbudget.rf._path_loss import slant_range

import json
import numpy as np


class TestRunLinkBudget:
    def test_basic_uhf_budget(self):
        req = LinkBudgetRequest(
            tx_power_dbm=33.0,
            tx_antenna_gain_dbi=5.15,
            rx_antenna_gain_dbi=14.0,
            rx_system_noise_temp_k=500.0,
            frequency_hz=437e6,
            distance_m=slant_range(500e3, 30.0),
            data_rate_bps=9600,
            modulation="BPSK",
            coding="convolutional_r12",
        )
        resp = run_link_budget(req)
        assert resp.link_closes
        assert resp.margin_db > 0
        assert resp.text_report != ""

    def test_response_fields_populated(self):
        req = LinkBudgetRequest(
            tx_power_dbm=33.0,
            tx_antenna_gain_dbi=5.15,
            rx_antenna_gain_dbi=14.0,
            rx_system_noise_temp_k=500.0,
            frequency_hz=437e6,
            distance_m=1000e3,
            data_rate_bps=9600,
        )
        resp = run_link_budget(req)
        assert resp.eirp_dbw != 0
        assert resp.free_space_path_loss_db > 0
        assert resp.c_over_n0_db_hz != 0


class TestRunPassSimulation:
    def test_preset_simulation(self):
        req = PassSimulationRequest(
            mission_preset="cubesat_uhf_downlink",
            duration_orbits=6,
            dt_s=5.0,
        )
        resp = run_pass_simulation(req)
        assert resp.num_passes >= 0
        assert resp.text_report != ""

    def test_invalid_preset(self):
        req = PassSimulationRequest(mission_preset="nonexistent_mission")
        with pytest.raises(ConfigurationError):
            run_pass_simulation(req)

    def test_no_input_raises(self):
        req = PassSimulationRequest()
        with pytest.raises(ConfigurationError):
            run_pass_simulation(req)


class TestComponentAPI:
    def test_list_transceivers(self):
        names = list_components("transceivers")
        assert len(names) == 5

    def test_get_transceiver(self):
        data = get_component("transceivers", "endurosat_uhf_transceiver_ii")
        assert data["name"] == "Endurosat UHF Transceiver II"

    def test_get_unknown_raises(self):
        with pytest.raises(ComponentNotFoundError):
            get_component("transceivers", "nonexistent")

    def test_get_presets(self):
        presets = get_presets()
        assert len(presets) == 5
        assert "cubesat_uhf_downlink" in presets


class TestSerializers:
    def test_numpy_encoder(self):
        data = {"val": np.float64(3.14), "arr": np.array([1, 2, 3])}
        result = json.dumps(data, cls=NumpyEncoder)
        assert "3.14" in result

    def test_serialize_results(self):
        data = {"margin": np.float64(10.5)}
        s = serialize_results(data)
        assert "10.5" in s
