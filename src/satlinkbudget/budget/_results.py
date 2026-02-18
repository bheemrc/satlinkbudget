"""Link budget result with waterfall plotting."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass
class LinkBudgetResult:
    """Complete line-item link budget result."""

    # Transmitter
    tx_power_dbw: float = 0.0
    tx_antenna_gain_dbi: float = 0.0
    tx_feed_loss_db: float = 0.0
    tx_pointing_loss_db: float = 0.0
    tx_other_loss_db: float = 0.0
    eirp_dbw: float = 0.0

    # Path
    frequency_hz: float = 0.0
    distance_m: float = 0.0
    free_space_path_loss_db: float = 0.0
    atmospheric_loss_db: float = 0.0
    polarization_loss_db: float = 0.0
    misc_loss_db: float = 0.0

    # Receiver
    rx_antenna_gain_dbi: float = 0.0
    rx_feed_loss_db: float = 0.0
    rx_pointing_loss_db: float = 0.0
    rx_other_loss_db: float = 0.0
    system_noise_temp_k: float = 0.0
    figure_of_merit_db_per_k: float = 0.0

    # Modem
    data_rate_bps: float = 0.0
    required_eb_n0_db: float = 0.0

    # Results
    c_over_n0_db_hz: float = 0.0
    eb_n0_db: float = 0.0
    margin_db: float = 0.0

    @property
    def link_closes(self) -> bool:
        """True if link margin is non-negative."""
        return self.margin_db >= 0.0

    def summary(self) -> dict[str, float]:
        """Key results as dictionary."""
        return {
            "eirp_dbw": self.eirp_dbw,
            "fspl_db": self.free_space_path_loss_db,
            "atmospheric_loss_db": self.atmospheric_loss_db,
            "figure_of_merit_db_per_k": self.figure_of_merit_db_per_k,
            "c_over_n0_db_hz": self.c_over_n0_db_hz,
            "eb_n0_db": self.eb_n0_db,
            "required_eb_n0_db": self.required_eb_n0_db,
            "margin_db": self.margin_db,
            "link_closes": float(self.link_closes),
        }

    def to_text(self) -> str:
        """Human-readable link budget table."""
        lines = [
            "=" * 60,
            "LINK BUDGET ANALYSIS",
            "=" * 60,
            "",
            "TRANSMITTER",
            f"  TX Power:            {self.tx_power_dbw:+8.2f} dBW",
            f"  TX Antenna Gain:     {self.tx_antenna_gain_dbi:+8.2f} dBi",
            f"  TX Feed Loss:        {-self.tx_feed_loss_db:+8.2f} dB",
            f"  TX Pointing Loss:    {-self.tx_pointing_loss_db:+8.2f} dB",
            f"  EIRP:                {self.eirp_dbw:+8.2f} dBW",
            "",
            "PATH",
            f"  Frequency:           {self.frequency_hz/1e9:8.3f} GHz",
            f"  Distance:            {self.distance_m/1e3:8.1f} km",
            f"  FSPL:                {-self.free_space_path_loss_db:+8.2f} dB",
            f"  Atmospheric Loss:    {-self.atmospheric_loss_db:+8.2f} dB",
            f"  Polarization Loss:   {-self.polarization_loss_db:+8.2f} dB",
            "",
            "RECEIVER",
            f"  RX Antenna Gain:     {self.rx_antenna_gain_dbi:+8.2f} dBi",
            f"  RX Feed Loss:        {-self.rx_feed_loss_db:+8.2f} dB",
            f"  RX Pointing Loss:    {-self.rx_pointing_loss_db:+8.2f} dB",
            f"  System Noise Temp:   {self.system_noise_temp_k:8.1f} K",
            f"  G/T:                 {self.figure_of_merit_db_per_k:+8.2f} dB/K",
            "",
            "LINK PERFORMANCE",
            f"  C/N₀:                {self.c_over_n0_db_hz:+8.2f} dB-Hz",
            f"  Data Rate:           {self.data_rate_bps:8.0f} bps",
            f"  Eb/N₀ (received):    {self.eb_n0_db:+8.2f} dB",
            f"  Eb/N₀ (required):    {self.required_eb_n0_db:+8.2f} dB",
            f"  MARGIN:              {self.margin_db:+8.2f} dB",
            f"  Link Closes:         {'YES' if self.link_closes else 'NO'}",
            "=" * 60,
        ]
        return "\n".join(lines)

    def plot_waterfall(self) -> Any:
        """Generate waterfall chart of link budget.

        Returns matplotlib Figure.
        """
        import matplotlib.pyplot as plt

        items = [
            ("TX Power", self.tx_power_dbw),
            ("TX Gain", self.tx_antenna_gain_dbi),
            ("TX Losses", -(self.tx_feed_loss_db + self.tx_pointing_loss_db + self.tx_other_loss_db)),
            ("FSPL", -self.free_space_path_loss_db),
            ("Atm. Loss", -self.atmospheric_loss_db),
            ("Pol. Loss", -self.polarization_loss_db),
            ("RX Gain", self.rx_antenna_gain_dbi),
            ("RX Losses", -(self.rx_feed_loss_db + self.rx_pointing_loss_db + self.rx_other_loss_db)),
            ("Boltzmann", 228.6),  # -k_B in dBW
            ("T_sys", -10.0 * np.log10(self.system_noise_temp_k)),
            ("Data Rate", -10.0 * np.log10(self.data_rate_bps) if self.data_rate_bps > 0 else 0),
        ]

        labels = [i[0] for i in items]
        values = [i[1] for i in items]

        fig, ax = plt.subplots(1, 1, figsize=(12, 6))

        cumulative = 0.0
        bottoms = []
        for v in values:
            bottoms.append(cumulative)
            cumulative += v

        colors = ["green" if v >= 0 else "red" for v in values]
        ax.bar(labels, values, bottom=bottoms, color=colors, alpha=0.7, edgecolor="black")

        # Add margin bar
        labels.append("Margin")
        ax.bar(
            ["Margin"],
            [self.margin_db],
            bottom=[0],
            color="blue" if self.margin_db >= 0 else "red",
            alpha=0.7,
            edgecolor="black",
        )

        ax.set_ylabel("dB")
        ax.set_title("Link Budget Waterfall")
        ax.tick_params(axis="x", rotation=45)
        fig.tight_layout()

        return fig
