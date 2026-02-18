#!/usr/bin/env python3
"""BER comparison across modulation schemes.

Plots BER vs Eb/N₀ for BPSK, QPSK, 8PSK, and 16QAM
on a semi-logarithmic scale. Annotates the required
Eb/N₀ for each scheme at BER = 10⁻⁵.
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from satlinkbudget.modem import BPSK, QPSK, PSK8, QAM16

# --- Sweep Eb/N₀ from 0 to 20 dB ---
eb_n0_db = np.linspace(0, 20, 500)

schemes = [
    (BPSK, "BPSK", "b-"),
    (QPSK, "QPSK", "g--"),
    (PSK8, "8PSK", "r-.", ),
    (QAM16, "16QAM", "m:"),
]

TARGET_BER = 1e-5

fig, ax = plt.subplots(figsize=(10, 6))

for scheme, label, style in schemes:
    ber_values = [scheme.ber(x) for x in eb_n0_db]
    ax.semilogy(eb_n0_db, ber_values, style, linewidth=2, label=label)

    # Find and annotate required Eb/N₀
    req = scheme.required_eb_n0_db(TARGET_BER)
    ax.plot(req, TARGET_BER, "ko", markersize=6)
    ax.annotate(
        f"{req:.1f} dB",
        xy=(req, TARGET_BER),
        xytext=(req + 0.8, TARGET_BER * 5),
        fontsize=9,
        arrowprops=dict(arrowstyle="->", color="gray"),
    )

# Target BER line
ax.axhline(y=TARGET_BER, color="gray", linestyle="--", alpha=0.6, label=f"BER = {TARGET_BER:.0e}")

ax.set_xlabel("Eb/N₀ [dB]", fontsize=12)
ax.set_ylabel("Bit Error Rate", fontsize=12)
ax.set_title("BER vs Eb/N₀ — Modulation Scheme Comparison", fontsize=13)
ax.set_ylim(1e-8, 1.0)
ax.set_xlim(0, 20)
ax.grid(True, which="both", alpha=0.3)
ax.legend(fontsize=11, loc="upper right")
fig.tight_layout()

# --- Save ---
IMAGES_DIR = Path(__file__).resolve().parent.parent / "docs" / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
fig.savefig(IMAGES_DIR / "ber_curves.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"Saved: {IMAGES_DIR / 'ber_curves.png'}")
