#!/usr/bin/env python3
"""Waterfall chart of a UHF CubeSat link budget.

Shows cumulative gain/loss contributions from TX power through to
link margin as a waterfall bar chart.
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from satlinkbudget.budget import (
    TransmitterChain,
    ReceiverChain,
    compute_link_budget,
)
from satlinkbudget.modem import BPSK, CONV_R12_K7, ModemConfig
from satlinkbudget.rf import slant_range

# --- Build the same UHF CubeSat link ---
tx = TransmitterChain.from_power_dbm(
    power_dbm=33.0,
    antenna_gain_dbi=5.15,
    feed_loss_db=0.5,
    pointing_loss_db=1.0,
)

rx = ReceiverChain(
    antenna_gain_dbi=14.0,
    system_noise_temp_k=500.0,
    feed_loss_db=0.3,
)

modem = ModemConfig(modulation=BPSK, coding=CONV_R12_K7, implementation_loss_db=1.0)
distance_m = slant_range(500e3, 30.0)

result = compute_link_budget(
    transmitter=tx,
    receiver=rx,
    frequency_hz=437e6,
    distance_m=distance_m,
    data_rate_bps=9600,
    required_eb_n0_db=modem.required_eb_n0_db(),
    atmospheric_loss_db=0.5,
)

# --- Generate and save waterfall chart ---
fig = result.plot_waterfall()

IMAGES_DIR = Path(__file__).resolve().parent.parent / "docs" / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
fig.savefig(IMAGES_DIR / "waterfall_chart.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"Saved: {IMAGES_DIR / 'waterfall_chart.png'}")
print(f"Link margin: {result.margin_db:+.2f} dB — {'CLOSES' if result.link_closes else 'FAILS'}")
