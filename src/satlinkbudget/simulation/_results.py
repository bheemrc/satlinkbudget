"""Pass simulation results and plotting."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass
class PassData:
    """Data from a single satellite pass."""

    pass_number: int
    start_time_s: float
    end_time_s: float
    duration_s: float
    max_elevation_deg: float
    times_s: np.ndarray
    elevations_deg: np.ndarray
    ranges_m: np.ndarray
    margins_db: np.ndarray
    cn0_db_hz: np.ndarray
    doppler_shifts_hz: np.ndarray
    data_rates_bps: np.ndarray
    data_volume_bits: float

    @property
    def data_volume_bytes(self) -> float:
        return self.data_volume_bits / 8.0

    @property
    def data_volume_kbytes(self) -> float:
        return self.data_volume_bits / 8.0 / 1024.0

    @property
    def min_margin_db(self) -> float:
        return float(np.min(self.margins_db))

    @property
    def max_margin_db(self) -> float:
        return float(np.max(self.margins_db))


@dataclass
class PassSimulationResults:
    """Aggregate results from pass simulation."""

    passes: list[PassData] = field(default_factory=list)
    total_data_volume_bits: float = 0.0
    total_contact_time_s: float = 0.0
    simulation_duration_s: float = 0.0
    num_passes: int = 0
    frequency_hz: float = 0.0
    data_rate_bps: float = 0.0

    @property
    def total_data_volume_bytes(self) -> float:
        return self.total_data_volume_bits / 8.0

    @property
    def total_data_volume_mbytes(self) -> float:
        return self.total_data_volume_bits / 8.0 / 1e6

    @property
    def passes_per_day(self) -> float:
        if self.simulation_duration_s <= 0:
            return 0.0
        return self.num_passes * 86400.0 / self.simulation_duration_s

    @property
    def avg_pass_duration_s(self) -> float:
        if self.num_passes == 0:
            return 0.0
        return self.total_contact_time_s / self.num_passes

    def plot_pass_elevation(self, pass_idx: int = 0) -> Any:
        """Plot elevation angle vs time for a specific pass."""
        import matplotlib.pyplot as plt

        p = self.passes[pass_idx]
        fig, ax = plt.subplots(figsize=(10, 4))
        t_min = (p.times_s - p.times_s[0]) / 60.0
        ax.plot(t_min, p.elevations_deg, "b-")
        ax.set_xlabel("Time [min]")
        ax.set_ylabel("Elevation [deg]")
        ax.set_title(f"Pass {p.pass_number} - Elevation")
        ax.grid(True)
        fig.tight_layout()
        return fig

    def plot_pass_margin(self, pass_idx: int = 0) -> Any:
        """Plot link margin vs time for a specific pass."""
        import matplotlib.pyplot as plt

        p = self.passes[pass_idx]
        fig, ax = plt.subplots(figsize=(10, 4))
        t_min = (p.times_s - p.times_s[0]) / 60.0
        ax.plot(t_min, p.margins_db, "g-")
        ax.axhline(y=0, color="r", linestyle="--", label="0 dB margin")
        ax.set_xlabel("Time [min]")
        ax.set_ylabel("Link Margin [dB]")
        ax.set_title(f"Pass {p.pass_number} - Link Margin")
        ax.legend()
        ax.grid(True)
        fig.tight_layout()
        return fig

    def plot_doppler(self, pass_idx: int = 0) -> Any:
        """Plot Doppler shift vs time for a specific pass."""
        import matplotlib.pyplot as plt

        p = self.passes[pass_idx]
        fig, ax = plt.subplots(figsize=(10, 4))
        t_min = (p.times_s - p.times_s[0]) / 60.0
        ax.plot(t_min, p.doppler_shifts_hz / 1e3, "m-")
        ax.set_xlabel("Time [min]")
        ax.set_ylabel("Doppler Shift [kHz]")
        ax.set_title(f"Pass {p.pass_number} - Doppler Shift")
        ax.grid(True)
        fig.tight_layout()
        return fig

    def plot_data_volume_cumulative(self) -> Any:
        """Plot cumulative data volume across all passes."""
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(10, 4))
        cumulative = 0.0
        for p in self.passes:
            t_hr = p.start_time_s / 3600.0
            ax.bar(t_hr, p.data_volume_bits / 8.0 / 1024.0, width=0.1, color="blue", alpha=0.7)
            cumulative += p.data_volume_bits / 8.0 / 1024.0

        ax.set_xlabel("Time [hours]")
        ax.set_ylabel("Data Volume [KB]")
        ax.set_title("Data Volume per Pass")
        ax.grid(True)
        fig.tight_layout()
        return fig
