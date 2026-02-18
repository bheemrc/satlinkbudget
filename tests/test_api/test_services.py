"""Tests for SaaS API services."""

import json

import numpy as np
import pytest

from satlinkbudget.api._schemas import (
    LinkBudgetRequest,
    MaxDataRateRequest,
    RequiredPowerRequest,
    PassSimulationRequest,
    PresetSimulationRequest,
    PlotFormat,
)
from satlinkbudget.api._services import (
    run_link_budget,
    run_max_data_rate,
    run_required_power,
    run_pass_simulation,
    run_preset,
    list_components,
    get_component,
    get_presets,
)
from satlinkbudget.api._errors import ConfigurationError, ComponentNotFoundError
from satlinkbudget.api._serializers import NumpyEncoder, serialize_results
from satlinkbudget.rf._path_loss import slant_range


# --- Link budget ---


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
        assert resp.summary.link_closes
        assert resp.summary.margin_db > 0
        assert resp.text_report != ""

    def test_response_has_simulation_id(self):
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
        assert len(resp.simulation_id) == 36  # UUID format

    def test_summary_fields_populated(self):
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
        s = resp.summary
        assert s.eirp_dbw != 0
        assert s.free_space_path_loss_db > 0
        assert s.c_over_n0_db_hz != 0
        assert s.figure_of_merit_db_per_k != 0

    def test_structured_waterfall(self):
        req = LinkBudgetRequest(
            tx_power_dbm=33.0,
            tx_antenna_gain_dbi=5.15,
            rx_antenna_gain_dbi=14.0,
            rx_system_noise_temp_k=500.0,
            frequency_hz=437e6,
            distance_m=1000e3,
            data_rate_bps=9600,
            plot_format=PlotFormat.STRUCTURED,
        )
        resp = run_link_budget(req)
        assert resp.waterfall_plot is not None
        assert resp.waterfall_plot.plot_type == "waterfall"
        assert resp.waterfall_plot.format == PlotFormat.STRUCTURED
        assert len(resp.waterfall_plot.time_series) == 8

    def test_png_waterfall(self):
        req = LinkBudgetRequest(
            tx_power_dbm=33.0,
            tx_antenna_gain_dbi=5.15,
            rx_antenna_gain_dbi=14.0,
            rx_system_noise_temp_k=500.0,
            frequency_hz=437e6,
            distance_m=1000e3,
            data_rate_bps=9600,
            plot_format=PlotFormat.PNG_BASE64,
        )
        resp = run_link_budget(req)
        assert resp.waterfall_plot.format == PlotFormat.PNG_BASE64
        assert resp.waterfall_plot.png_base64 is not None
        assert len(resp.waterfall_plot.png_base64) > 100

    def test_misc_loss(self):
        req = LinkBudgetRequest(
            tx_power_dbm=33.0,
            tx_antenna_gain_dbi=5.15,
            rx_antenna_gain_dbi=14.0,
            rx_system_noise_temp_k=500.0,
            frequency_hz=437e6,
            distance_m=1000e3,
            data_rate_bps=9600,
            misc_loss_db=3.0,
        )
        resp = run_link_budget(req)
        assert resp.summary.misc_loss_db == 3.0


# --- Max data rate ---


class TestMaxDataRate:
    def test_positive_rate(self):
        req = MaxDataRateRequest(
            tx_power_dbm=33.0,
            tx_antenna_gain_dbi=5.15,
            rx_antenna_gain_dbi=14.0,
            rx_system_noise_temp_k=500.0,
            frequency_hz=437e6,
            distance_m=1000e3,
        )
        resp = run_max_data_rate(req)
        assert resp.max_data_rate_bps > 0
        assert resp.link_closes
        assert len(resp.simulation_id) == 36

    def test_kbps_conversion(self):
        req = MaxDataRateRequest(
            tx_power_dbm=33.0,
            tx_antenna_gain_dbi=5.15,
            rx_antenna_gain_dbi=14.0,
            rx_system_noise_temp_k=500.0,
            frequency_hz=437e6,
            distance_m=1000e3,
        )
        resp = run_max_data_rate(req)
        assert abs(resp.max_data_rate_kbps - resp.max_data_rate_bps / 1e3) < 0.01


# --- Required power ---


class TestRequiredPower:
    def test_reasonable_power(self):
        req = RequiredPowerRequest(
            rx_antenna_gain_dbi=14.0,
            rx_system_noise_temp_k=500.0,
            frequency_hz=437e6,
            distance_m=1000e3,
            data_rate_bps=9600,
        )
        resp = run_required_power(req)
        assert resp.required_power_dbm < 50  # less than 100 W
        assert resp.required_power_w > 0
        assert len(resp.simulation_id) == 36

    def test_dbm_dbw_conversion(self):
        req = RequiredPowerRequest(
            rx_antenna_gain_dbi=14.0,
            rx_system_noise_temp_k=500.0,
            frequency_hz=437e6,
            distance_m=1000e3,
            data_rate_bps=9600,
        )
        resp = run_required_power(req)
        assert abs(resp.required_power_dbm - (resp.required_power_dbw + 30.0)) < 0.01


# --- Pass simulation ---


class TestRunPassSimulation:
    def test_preset_simulation(self):
        req = PassSimulationRequest(
            mission_preset="cubesat_uhf_downlink",
            duration_orbits=6,
            dt_s=5.0,
            plot_format=PlotFormat.STRUCTURED,
        )
        resp = run_pass_simulation(req)
        assert resp.summary.num_passes >= 0
        assert resp.text_report != ""
        assert len(resp.simulation_id) == 36

    def test_per_pass_details(self):
        req = PassSimulationRequest(
            mission_preset="cubesat_uhf_downlink",
            duration_orbits=24,
            dt_s=5.0,
        )
        resp = run_pass_simulation(req)
        assert len(resp.passes) == resp.summary.num_passes
        if resp.passes:
            p = resp.passes[0]
            assert p.pass_number == 1
            assert p.duration_s > 0
            assert p.max_elevation_deg > 0
            assert p.data_volume_kbytes >= 0

    def test_structured_plots(self):
        req = PassSimulationRequest(
            mission_preset="cubesat_uhf_downlink",
            duration_orbits=24,
            dt_s=5.0,
            plot_format=PlotFormat.STRUCTURED,
        )
        resp = run_pass_simulation(req)
        plot_types = [p.plot_type for p in resp.plots]
        assert "data_volume" in plot_types
        if resp.summary.num_passes > 0:
            assert "elevation" in plot_types
            assert "margin" in plot_types
            assert "doppler" in plot_types

    def test_structured_plot_has_time_series(self):
        req = PassSimulationRequest(
            mission_preset="cubesat_uhf_downlink",
            duration_orbits=24,
            dt_s=5.0,
            plot_format=PlotFormat.STRUCTURED,
        )
        resp = run_pass_simulation(req)
        for plot in resp.plots:
            if plot.time_series:
                for ts in plot.time_series:
                    assert len(ts.x) == len(ts.y)
                    assert ts.label != ""
                    assert ts.unit != ""

    def test_invalid_preset(self):
        req = PassSimulationRequest(mission_preset="nonexistent_mission")
        with pytest.raises(ConfigurationError):
            run_pass_simulation(req)

    def test_no_input_raises(self):
        req = PassSimulationRequest()
        with pytest.raises(ConfigurationError):
            run_pass_simulation(req)


# --- Preset with overrides ---


class TestRunPreset:
    def test_basic_preset(self):
        req = PresetSimulationRequest(
            preset_name="cubesat_uhf_downlink",
            duration_orbits=6,
            dt_s=5.0,
        )
        resp = run_preset(req)
        assert resp.summary.num_passes >= 0
        assert len(resp.simulation_id) == 36

    def test_override_data_rate(self):
        req = PresetSimulationRequest(
            preset_name="cubesat_uhf_downlink",
            overrides={"modem": {"data_rate_bps": 19200}},
            duration_orbits=24,
            dt_s=5.0,
        )
        resp = run_preset(req)
        assert resp.summary.data_rate_bps == 19200

    def test_invalid_preset_raises(self):
        req = PresetSimulationRequest(preset_name="nonexistent")
        with pytest.raises(ConfigurationError):
            run_preset(req)


# --- Component API ---


class TestComponentAPI:
    def test_list_transceivers(self):
        resp = list_components("transceivers")
        assert resp.category == "transceivers"
        assert len(resp.components) == 5

    def test_list_antennas(self):
        resp = list_components("antennas")
        assert resp.category == "antennas"
        assert len(resp.components) > 0

    def test_list_groundstations(self):
        resp = list_components("groundstations")
        assert resp.category == "groundstations"
        assert len(resp.components) > 0

    def test_component_highlights(self):
        resp = list_components("transceivers")
        comp = resp.components[0]
        assert comp.name != ""
        assert "tx_power_dbm" in comp.highlights

    def test_get_transceiver(self):
        resp = get_component("transceivers", "endurosat_uhf_transceiver_ii")
        assert resp.name == "endurosat_uhf_transceiver_ii"
        assert resp.category == "transceivers"
        assert "name" in resp.data

    def test_get_unknown_raises(self):
        with pytest.raises(ComponentNotFoundError):
            get_component("transceivers", "nonexistent")

    def test_get_presets(self):
        resp = get_presets()
        assert len(resp.presets) == 5
        names = [p.name for p in resp.presets]
        assert "cubesat_uhf_downlink" in names

    def test_unknown_category_raises(self):
        with pytest.raises(ComponentNotFoundError):
            list_components("nonexistent_category")


# --- Serializers ---


class TestSerializers:
    def test_numpy_encoder(self):
        data = {"val": np.float64(3.14), "arr": np.array([1, 2, 3])}
        result = json.dumps(data, cls=NumpyEncoder)
        assert "3.14" in result

    def test_serialize_results(self):
        data = {"margin": np.float64(10.5)}
        s = serialize_results(data)
        assert "10.5" in s


# --- Input validation ---


class TestInputValidation:
    def test_budget_validates_frequency(self):
        req = LinkBudgetRequest(
            tx_power_dbm=33.0,
            tx_antenna_gain_dbi=5.15,
            rx_antenna_gain_dbi=14.0,
            rx_system_noise_temp_k=500.0,
            frequency_hz=437e6,
            distance_m=1000e3,
            data_rate_bps=9600,
        )
        # Valid request should work
        resp = run_link_budget(req)
        assert resp.summary.link_closes is not None

    def test_budget_rejects_negative_frequency(self):
        with pytest.raises(Exception):
            LinkBudgetRequest(
                tx_power_dbm=33.0,
                tx_antenna_gain_dbi=5.15,
                rx_antenna_gain_dbi=14.0,
                rx_system_noise_temp_k=500.0,
                frequency_hz=-1.0,
                distance_m=1000e3,
                data_rate_bps=9600,
            )

    def test_budget_rejects_zero_distance(self):
        with pytest.raises(Exception):
            LinkBudgetRequest(
                tx_power_dbm=33.0,
                tx_antenna_gain_dbi=5.15,
                rx_antenna_gain_dbi=14.0,
                rx_system_noise_temp_k=500.0,
                frequency_hz=437e6,
                distance_m=0.0,
                data_rate_bps=9600,
            )
