#!/usr/bin/env python3
"""Quick-start example: UHF CubeSat downlink link budget.

Endurosat UHF II (33 dBm / 2W) → monopole (5.15 dBi)
  ↓ Free-space channel @ 437 MHz, 500 km, 30° elevation
Yagi ground (14 dBi) → BPSK + Conv R=1/2 @ 9600 bps
"""

from satlinkbudget.budget import (
    TransmitterChain,
    ReceiverChain,
    compute_link_budget,
    compute_max_data_rate,
    compute_required_power_dbw,
)
from satlinkbudget.modem import BPSK, CONV_R12_K7, ModemConfig
from satlinkbudget.rf import slant_range

# --- Parameters ---
FREQUENCY_HZ = 437e6        # UHF amateur band
ALTITUDE_M = 500e3           # 500 km LEO
ELEVATION_DEG = 30.0         # mid-pass elevation
DATA_RATE_BPS = 9600.0       # 9.6 kbps BPSK

# --- Transmitter chain (satellite) ---
tx = TransmitterChain.from_power_dbm(
    power_dbm=33.0,              # Endurosat UHF II: 2W
    antenna_gain_dbi=5.15,       # quarter-wave monopole
    feed_loss_db=0.5,
    pointing_loss_db=1.0,        # 5° error on ~45° beamwidth
)

# --- Receiver chain (ground station) ---
rx = ReceiverChain(
    antenna_gain_dbi=14.0,       # 10-element UHF Yagi
    system_noise_temp_k=500.0,   # warm ground + LNA
    feed_loss_db=0.3,
)

# --- Modem ---
modem = ModemConfig(
    modulation=BPSK,
    coding=CONV_R12_K7,          # convolutional R=1/2, K=7
    implementation_loss_db=1.0,
)
required_eb_n0 = modem.required_eb_n0_db()

# --- Geometry ---
distance_m = slant_range(ALTITUDE_M, ELEVATION_DEG)

# --- Compute link budget ---
result = compute_link_budget(
    transmitter=tx,
    receiver=rx,
    frequency_hz=FREQUENCY_HZ,
    distance_m=distance_m,
    data_rate_bps=DATA_RATE_BPS,
    required_eb_n0_db=required_eb_n0,
    atmospheric_loss_db=0.5,       # small at UHF
)

# --- Print full report ---
print(result.to_text())
print()

# --- Additional analyses ---
max_rate = compute_max_data_rate(
    transmitter=tx,
    receiver=rx,
    frequency_hz=FREQUENCY_HZ,
    distance_m=distance_m,
    required_eb_n0_db=required_eb_n0,
    target_margin_db=3.0,
    atmospheric_loss_db=0.5,
)
print(f"Maximum data rate with 3 dB margin: {max_rate:,.0f} bps")

min_power = compute_required_power_dbw(
    receiver=rx,
    frequency_hz=FREQUENCY_HZ,
    distance_m=distance_m,
    data_rate_bps=DATA_RATE_BPS,
    required_eb_n0_db=required_eb_n0,
    target_margin_db=3.0,
    tx_antenna_gain_dbi=5.15,
    tx_feed_loss_db=0.5,
    atmospheric_loss_db=0.5,
)
print(f"Minimum TX power for 3 dB margin: {min_power:+.1f} dBW ({10**(min_power/10)*1e3:.0f} mW)")
