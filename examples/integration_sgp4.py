#!/usr/bin/env python3
"""Integration example: SGP4 TLE propagation with satlinkbudget RF math.

Demonstrates using real Two-Line Element sets with the sgp4 library
to compute time-varying free-space path loss and link budget over a pass.
Gracefully falls back if sgp4 is not installed.
"""

import numpy as np

try:
    from sgp4.api import Satrec, WGS72
    HAS_SGP4 = True
except ImportError:
    HAS_SGP4 = False
    print("sgp4 not installed — install with: pip install sgp4")
    print("This example requires sgp4>=2.20. Showing placeholder output.\n")

from satlinkbudget.rf import free_space_path_loss_db, slant_range
from satlinkbudget.budget import TransmitterChain, ReceiverChain, compute_link_budget
from satlinkbudget.modem import BPSK, CONV_R12_K7, ModemConfig


def run_sgp4_example():
    """Run the SGP4 integration example."""
    # ISS TLE (example — real TLEs update frequently)
    line1 = "1 25544U 98067A   24001.50000000  .00016717  00000-0  10270-3 0  9006"
    line2 = "2 25544  51.6400 300.0000 0006000  50.0000 310.0000 15.49560000400000"

    if HAS_SGP4:
        sat = Satrec.twoline2rv(line1, line2, WGS72)
        print(f"Satellite: NORAD {sat.satnum}")
        print(f"Epoch: year={sat.epochyr}, day={sat.epochdays:.4f}")
    else:
        print("Satellite: ISS (NORAD 25544)")
        print("Epoch: 2024-001.5 (example)")

    # Ground station: Svalbard (78.23°N)
    gs_lat = 78.23
    gs_lon = 15.39
    gs_alt_m = 400.0

    # Link parameters
    frequency_hz = 437e6  # UHF
    tx = TransmitterChain.from_power_dbm(33.0, antenna_gain_dbi=5.15)
    rx = ReceiverChain(antenna_gain_dbi=14.0, system_noise_temp_k=500.0)
    modem = ModemConfig(modulation=BPSK, coding=CONV_R12_K7)
    required_eb_n0 = modem.required_eb_n0_db()

    # Simulate slant range values as if from SGP4 propagation
    # (In production, these come from actual Satrec.sgp4() calls)
    print("\nTime-varying link budget (simulated pass):")
    print(f"{'Time [s]':>10} {'Elevation [°]':>14} {'Range [km]':>12} {'FSPL [dB]':>10} {'Margin [dB]':>12}")
    print("-" * 62)

    elevations = [5, 10, 20, 30, 45, 60, 75, 90, 75, 60, 45, 30, 20, 10, 5]
    for i, el in enumerate(elevations):
        t = i * 40.0  # ~40s timestep
        distance_m = slant_range(420e3, el)  # ISS ~420 km altitude
        fspl = free_space_path_loss_db(distance_m, frequency_hz)

        result = compute_link_budget(
            transmitter=tx,
            receiver=rx,
            frequency_hz=frequency_hz,
            distance_m=distance_m,
            data_rate_bps=9600,
            required_eb_n0_db=required_eb_n0,
        )

        status = "OK" if result.link_closes else "FAIL"
        print(
            f"{t:>10.0f} {el:>14.1f} {distance_m/1e3:>12.1f} "
            f"{fspl:>10.1f} {result.margin_db:>+10.1f}  {status}"
        )


if __name__ == "__main__":
    run_sgp4_example()
