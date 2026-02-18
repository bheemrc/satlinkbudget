#!/usr/bin/env python3
"""Antenna comparison: parabolic dish gain vs frequency.

Plots gain curves for 2.4m, 3.7m, 7.3m, and 13m parabolic
dishes from 1 GHz to 30 GHz (typical ground station sizes).
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from satlinkbudget.antenna import ParabolicAntenna

IMAGES_DIR = Path(__file__).resolve().parent.parent / "docs" / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# --- Dish configurations ---
dishes = [
    ParabolicAntenna(diameter_m=2.4, efficiency=0.55, name="2.4 m"),
    ParabolicAntenna(diameter_m=3.7, efficiency=0.55, name="3.7 m"),
    ParabolicAntenna(diameter_m=7.3, efficiency=0.55, name="7.3 m"),
    ParabolicAntenna(diameter_m=13.0, efficiency=0.55, name="13 m (DSN)"),
]
styles = ["b-", "g--", "r-.", "m:"]

# --- Frequency sweep ---
freqs_ghz = np.linspace(1, 30, 300)
freqs_hz = freqs_ghz * 1e9

fig, ax = plt.subplots(figsize=(10, 6))

for dish, style in zip(dishes, styles):
    gains = [dish.gain_db(f) for f in freqs_hz]
    ax.plot(freqs_ghz, gains, style, linewidth=2, label=dish.name)

ax.set_xlabel("Frequency [GHz]", fontsize=12)
ax.set_ylabel("Antenna Gain [dBi]", fontsize=12)
ax.set_title("Parabolic Dish Gain vs Frequency (η = 0.55)", fontsize=13)
ax.grid(True, alpha=0.3)
ax.legend(fontsize=11)
fig.tight_layout()

fig.savefig(IMAGES_DIR / "antenna_gain_vs_frequency.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"Saved: {IMAGES_DIR / 'antenna_gain_vs_frequency.png'}")
