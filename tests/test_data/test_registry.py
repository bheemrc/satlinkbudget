"""Tests for component registry and YAML loading."""

import pytest

from satlinkbudget.data._registry import ComponentRegistry, registry


class TestRegistry:
    def test_list_transceivers(self):
        names = registry.list_transceivers()
        assert len(names) == 5
        assert "endurosat_uhf_transceiver_ii" in names

    def test_get_transceiver(self):
        tx = registry.get_transceiver("endurosat_uhf_transceiver_ii")
        assert tx.name == "Endurosat UHF Transceiver II"
        assert tx.frequency_hz == pytest.approx(437e6)
        assert tx.tx_power_dbm == pytest.approx(33.0)

    def test_get_transceiver_not_found(self):
        with pytest.raises(KeyError, match="not found"):
            registry.get_transceiver("nonexistent")

    def test_list_antennas(self):
        names = registry.list_antennas()
        assert len(names) == 10
        assert "parabolic_3_7m" in names

    def test_get_antenna(self):
        ant = registry.get_antenna("parabolic_3_7m")
        assert ant.type == "parabolic"
        assert ant.diameter_m == pytest.approx(3.7)

    def test_list_groundstations(self):
        names = registry.list_groundstations()
        assert len(names) == 9
        assert "ksat_svalbard" in names

    def test_get_groundstation(self):
        gs = registry.get_groundstation("ksat_svalbard")
        assert gs.latitude_deg == pytest.approx(78.23)
        assert gs.operator == "KSAT"

    def test_list_bands(self):
        names = registry.list_bands()
        assert len(names) == 7
        assert "uhf" in names

    def test_get_band(self):
        band = registry.get_band("x_band")
        assert band.designation == "X"
        assert band.downlink_min_hz > 0

    def test_all_transceivers_parse(self):
        for name in registry.list_transceivers():
            tx = registry.get_transceiver(name)
            assert tx.frequency_hz > 0
            assert tx.tx_power_dbm != 0

    def test_all_antennas_parse(self):
        for name in registry.list_antennas():
            ant = registry.get_antenna(name)
            assert ant.type in {"parabolic", "patch", "helix", "dipole", "monopole", "horn", "yagi"}

    def test_all_groundstations_parse(self):
        for name in registry.list_groundstations():
            gs = registry.get_groundstation(name)
            assert -90 <= gs.latitude_deg <= 90
            assert -180 <= gs.longitude_deg <= 180

    def test_all_bands_parse(self):
        for name in registry.list_bands():
            band = registry.get_band(name)
            assert band.designation != ""

    def test_list_category(self):
        assert registry.list_category("transceivers") == registry.list_transceivers()

    def test_clear_cache(self):
        registry.list_transceivers()  # populate cache
        registry.clear_cache()
        names = registry.list_transceivers()  # should re-discover
        assert len(names) == 5
