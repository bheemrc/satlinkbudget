#!/usr/bin/env python3
"""Atmospheric loss plots: loss vs frequency and loss vs elevation.

Plot 1: Total and component atmospheric losses from 0.1–50 GHz at 30° elevation.
Plot 2: Losses vs elevation from 5°–90° at 10 GHz.
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from satlinkbudget.atmosphere import compute_atmospheric_losses

IMAGES_DIR = Path(__file__).resolve().parent.parent / "docs" / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# Plot 1: Atmospheric loss vs frequency at 30° elevation
# ============================================================
freqs_ghz = np.logspace(-1, np.log10(50), 300)  # 0.1 – 50 GHz
elevation_deg = 30.0

gaseous = np.zeros_like(freqs_ghz)
rain = np.zeros_like(freqs_ghz)
cloud = np.zeros_like(freqs_ghz)
total = np.zeros_like(freqs_ghz)

for i, f in enumerate(freqs_ghz):
    losses = compute_atmospheric_losses(
        freq_ghz=f,
        elevation_deg=elevation_deg,
        rain_rate_001_mm_h=25.0,         # moderate rain (ITU-R rain zone K)
        liquid_water_content_kg_m2=0.3,   # moderate cloud cover
    )
    gaseous[i] = losses.gaseous_db
    rain[i] = losses.rain_db
    cloud[i] = losses.cloud_db
    total[i] = losses.total_db

fig1, ax1 = plt.subplots(figsize=(10, 6))
ax1.semilogx(freqs_ghz, gaseous, "b-", linewidth=1.5, label="Gaseous (P.676)")
ax1.semilogx(freqs_ghz, rain, "r--", linewidth=1.5, label="Rain (P.618/P.838)")
ax1.semilogx(freqs_ghz, cloud, "g-.", linewidth=1.5, label="Cloud (P.840)")
ax1.semilogx(freqs_ghz, total, "k-", linewidth=2.0, label="Total")
ax1.set_xlabel("Frequency [GHz]", fontsize=12)
ax1.set_ylabel("Attenuation [dB]", fontsize=12)
ax1.set_title("Atmospheric Losses vs Frequency (El = 30°, R₀₀₁ = 25 mm/h)", fontsize=13)
ax1.grid(True, which="both", alpha=0.3)
ax1.legend(fontsize=11)
ax1.set_ylim(bottom=0)
fig1.tight_layout()

fig1.savefig(IMAGES_DIR / "atmospheric_vs_frequency.png", dpi=150, bbox_inches="tight")
plt.close(fig1)
print(f"Saved: {IMAGES_DIR / 'atmospheric_vs_frequency.png'}")

# ============================================================
# Plot 2: Atmospheric loss vs elevation at 10 GHz
# ============================================================
elevations = np.linspace(5, 90, 200)
freq_ghz = 10.0

gaseous_el = np.zeros_like(elevations)
rain_el = np.zeros_like(elevations)
cloud_el = np.zeros_like(elevations)
total_el = np.zeros_like(elevations)

for i, el in enumerate(elevations):
    losses = compute_atmospheric_losses(
        freq_ghz=freq_ghz,
        elevation_deg=el,
        rain_rate_001_mm_h=25.0,
        liquid_water_content_kg_m2=0.3,
    )
    gaseous_el[i] = losses.gaseous_db
    rain_el[i] = losses.rain_db
    cloud_el[i] = losses.cloud_db
    total_el[i] = losses.total_db

fig2, ax2 = plt.subplots(figsize=(10, 6))
ax2.plot(elevations, gaseous_el, "b-", linewidth=1.5, label="Gaseous (P.676)")
ax2.plot(elevations, rain_el, "r--", linewidth=1.5, label="Rain (P.618/P.838)")
ax2.plot(elevations, cloud_el, "g-.", linewidth=1.5, label="Cloud (P.840)")
ax2.plot(elevations, total_el, "k-", linewidth=2.0, label="Total")
ax2.set_xlabel("Elevation Angle [degrees]", fontsize=12)
ax2.set_ylabel("Attenuation [dB]", fontsize=12)
ax2.set_title("Atmospheric Losses vs Elevation (f = 10 GHz, R₀₀₁ = 25 mm/h)", fontsize=13)
ax2.grid(True, alpha=0.3)
ax2.legend(fontsize=11)
ax2.set_ylim(bottom=0)
fig2.tight_layout()

fig2.savefig(IMAGES_DIR / "atmospheric_vs_elevation.png", dpi=150, bbox_inches="tight")
plt.close(fig2)
print(f"Saved: {IMAGES_DIR / 'atmospheric_vs_elevation.png'}")
