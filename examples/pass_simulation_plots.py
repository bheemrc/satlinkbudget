#!/usr/bin/env python3
"""Pass simulation with plot generation.

Runs a 24-orbit simulation using the cubesat_uhf_downlink preset,
then generates four diagnostic plots and the text report.
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from satlinkbudget.mission import load_mission, build_pass_simulation
from satlinkbudget.simulation._report import generate_report

# --- Load mission and build simulation ---
MISSION_DIR = Path(__file__).resolve().parent.parent / "src" / "satlinkbudget" / "data" / "missions"
config = load_mission(MISSION_DIR / "cubesat_uhf_downlink.yaml")
sim = build_pass_simulation(config)

# --- Run simulation ---
results = sim.run(
    duration_orbits=config.simulation.duration_orbits,
    dt_s=config.simulation.dt_s,
    contact_dt_s=config.simulation.contact_dt_s,
)

# --- Print text report ---
report = generate_report(results)
print(report)

# --- Generate plots ---
IMAGES_DIR = Path(__file__).resolve().parent.parent / "docs" / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

if results.num_passes > 0:
    # Find the pass with highest elevation for the best demonstration
    best_idx = max(range(results.num_passes), key=lambda i: results.passes[i].max_elevation_deg)

    fig = results.plot_pass_elevation(best_idx)
    fig.savefig(IMAGES_DIR / "pass_elevation.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"\nSaved: {IMAGES_DIR / 'pass_elevation.png'}")

    fig = results.plot_pass_margin(best_idx)
    fig.savefig(IMAGES_DIR / "pass_margin.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {IMAGES_DIR / 'pass_margin.png'}")

    fig = results.plot_doppler(best_idx)
    fig.savefig(IMAGES_DIR / "doppler_shift.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {IMAGES_DIR / 'doppler_shift.png'}")

    fig = results.plot_data_volume_cumulative()
    fig.savefig(IMAGES_DIR / "data_volume.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {IMAGES_DIR / 'data_volume.png'}")
else:
    print("\nNo passes found — cannot generate plots.")
