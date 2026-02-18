#!/usr/bin/env python3
"""Master script: generate all documentation images.

Runs all example scripts that produce plots, saving PNGs to docs/images/.
"""

import subprocess
import sys
from pathlib import Path

EXAMPLES_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = EXAMPLES_DIR.parent
IMAGES_DIR = PROJECT_ROOT / "docs" / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

PYTHON = sys.executable

SCRIPTS = [
    ("Waterfall chart", "waterfall_chart.py"),
    ("BER comparison curves", "ber_comparison.py"),
    ("Atmospheric effects", "atmospheric_effects.py"),
    ("Antenna gain comparison", "antenna_comparison.py"),
    ("Pass simulation plots", "pass_simulation_plots.py"),
]

print("=" * 60)
print("satlinkbudget — Generating documentation images")
print("=" * 60)

failures = []
for i, (desc, script) in enumerate(SCRIPTS, 1):
    print(f"\n[{i}/{len(SCRIPTS)}] {desc}...")
    result = subprocess.run(
        [PYTHON, str(EXAMPLES_DIR / script)],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode != 0:
        print(f"  FAILED: {result.stderr.strip().splitlines()[-1] if result.stderr.strip() else 'unknown error'}")
        failures.append(script)
    else:
        # Print saved file lines
        for line in result.stdout.strip().splitlines():
            if line.startswith("Saved:"):
                print(f"  {line}")

# --- Summary ---
print("\n" + "=" * 60)
generated = sorted(IMAGES_DIR.glob("*.png"))
print(f"Generated {len(generated)} images in docs/images/:")
for p in generated:
    print(f"  {p.name}")
if failures:
    print(f"\nFailed scripts: {', '.join(failures)}")
print("=" * 60)
