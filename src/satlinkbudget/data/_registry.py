"""Component registry with lazy glob discovery."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from satlinkbudget.data._loader import (
    AntennaData,
    FrequencyBandData,
    GroundStationData,
    TransceiverData,
)

_DATA_DIR = Path(__file__).parent


class ComponentRegistry:
    """Lazy-loading registry for YAML component datasheets."""

    def __init__(self, data_dir: Path | None = None) -> None:
        self._data_dir = data_dir or _DATA_DIR
        self._cache: dict[str, dict[str, Any]] = {}

    def _discover(self, category: str) -> dict[str, Path]:
        """Discover all YAML files in a category directory."""
        cat_dir = self._data_dir / category
        if not cat_dir.exists():
            return {}
        return {p.stem: p for p in sorted(cat_dir.glob("*.yaml"))}

    def _get_category_cache(self, category: str) -> dict[str, Path]:
        if category not in self._cache:
            self._cache[category] = self._discover(category)
        return self._cache[category]

    def list_transceivers(self) -> list[str]:
        return list(self._get_category_cache("transceivers").keys())

    def get_transceiver(self, name: str) -> TransceiverData:
        paths = self._get_category_cache("transceivers")
        if name not in paths:
            available = ", ".join(paths.keys())
            raise KeyError(f"Transceiver '{name}' not found. Available: {available}")
        return TransceiverData.from_yaml(paths[name])

    def list_antennas(self) -> list[str]:
        return list(self._get_category_cache("antennas").keys())

    def get_antenna(self, name: str) -> AntennaData:
        paths = self._get_category_cache("antennas")
        if name not in paths:
            available = ", ".join(paths.keys())
            raise KeyError(f"Antenna '{name}' not found. Available: {available}")
        return AntennaData.from_yaml(paths[name])

    def list_groundstations(self) -> list[str]:
        return list(self._get_category_cache("groundstations").keys())

    def get_groundstation(self, name: str) -> GroundStationData:
        paths = self._get_category_cache("groundstations")
        if name not in paths:
            available = ", ".join(paths.keys())
            raise KeyError(f"Ground station '{name}' not found. Available: {available}")
        return GroundStationData.from_yaml(paths[name])

    def list_bands(self) -> list[str]:
        return list(self._get_category_cache("bands").keys())

    def get_band(self, name: str) -> FrequencyBandData:
        paths = self._get_category_cache("bands")
        if name not in paths:
            available = ", ".join(paths.keys())
            raise KeyError(f"Frequency band '{name}' not found. Available: {available}")
        return FrequencyBandData.from_yaml(paths[name])

    def list_missions(self) -> list[str]:
        return list(self._get_category_cache("missions").keys())

    def list_category(self, category: str) -> list[str]:
        return list(self._get_category_cache(category).keys())

    def clear_cache(self) -> None:
        self._cache.clear()


# Singleton instance
registry = ComponentRegistry()
