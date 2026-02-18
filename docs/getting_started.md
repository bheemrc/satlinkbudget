# Getting Started

> **Usage note:** satlinkbudget is a development-stage library. Models are cross-checked against analytical references and textbook examples, but have not been validated against real mission data. Always independently verify results before relying on them for mission-critical decisions.

## Installation

### From PyPI (when published)

```bash
pip install satlinkbudget
```

### From source

```bash
git clone https://github.com/satlinkbudget/satlinkbudget.git
cd satlinkbudget
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Optional integrations

```bash
# SGP4 TLE propagation
pip install satlinkbudget[sgp4]

# Skyfield high-precision ephemerides
pip install satlinkbudget[skyfield]

# Everything
pip install satlinkbudget[all]
```

---

## Your First Link Budget

A link budget accounts for every gain and loss between a satellite transmitter and a ground station receiver. Here's a complete UHF CubeSat downlink analysis:

```python
from satlinkbudget.budget import (
    TransmitterChain,
    ReceiverChain,
    compute_link_budget,
)
from satlinkbudget.modem import BPSK, CONV_R12_K7, ModemConfig
from satlinkbudget.rf import slant_range

# Satellite transmitter: Endurosat UHF II (2W) + monopole antenna
tx = TransmitterChain.from_power_dbm(
    power_dbm=33.0,           # 2W = 33 dBm
    antenna_gain_dbi=5.15,    # quarter-wave monopole
    feed_loss_db=0.5,
    pointing_loss_db=1.0,
)

# Ground station receiver: UHF Yagi + warm system
rx = ReceiverChain(
    antenna_gain_dbi=14.0,    # 10-element Yagi
    system_noise_temp_k=500.0,
    feed_loss_db=0.3,
)

# Modem: BPSK + convolutional R=1/2 K=7
modem = ModemConfig(modulation=BPSK, coding=CONV_R12_K7)
required_eb_n0 = modem.required_eb_n0_db()

# Geometry: 500 km altitude, 30° elevation
distance_m = slant_range(500e3, 30.0)

# Compute full link budget
result = compute_link_budget(
    transmitter=tx,
    receiver=rx,
    frequency_hz=437e6,
    distance_m=distance_m,
    data_rate_bps=9600,
    required_eb_n0_db=required_eb_n0,
    atmospheric_loss_db=0.5,
)

print(result.to_text())
```

**Output:**

```
============================================================
LINK BUDGET ANALYSIS
============================================================

TRANSMITTER
  TX Power:               +3.00 dBW
  TX Antenna Gain:        +5.15 dBi
  TX Feed Loss:           -0.50 dB
  TX Pointing Loss:       -1.00 dB
  EIRP:                   +6.65 dBW

PATH
  Frequency:              0.437 GHz
  Distance:               909.5 km
  FSPL:                 -144.43 dB
  Atmospheric Loss:       -0.50 dB
  Polarization Loss:      -0.00 dB

RECEIVER
  RX Antenna Gain:       +14.00 dBi
  RX Feed Loss:           -0.30 dB
  RX Pointing Loss:       -0.00 dB
  System Noise Temp:      500.0 K
  G/T:                   -13.29 dB/K

LINK PERFORMANCE
  C/N₀:                  +77.03 dB-Hz
  Data Rate:               9600 bps
  Eb/N₀ (received):      +37.20 dB
  Eb/N₀ (required):       +5.59 dB
  MARGIN:                +31.62 dB
  Link Closes:         YES
============================================================
```

---

## Your First Pass Simulation

satlinkbudget can simulate link performance over complete satellite passes, accounting for time-varying elevation, range, atmospheric losses, and Doppler shift.

The fastest way is to use a mission preset:

```python
from pathlib import Path
from satlinkbudget.mission import load_mission, build_pass_simulation
from satlinkbudget.simulation._report import generate_report

# Load the built-in CubeSat UHF downlink preset
config = load_mission("src/satlinkbudget/data/missions/cubesat_uhf_downlink.yaml")

# Build and run 24-orbit simulation
sim = build_pass_simulation(config)
results = sim.run(duration_orbits=24, dt_s=1.0)

# Print the report
print(generate_report(results))

# Plot the highest-elevation pass
fig = results.plot_pass_elevation(0)
fig = results.plot_pass_margin(0)
fig = results.plot_doppler(0)
fig = results.plot_data_volume_cumulative()
```

---

## Using the CLI

### List available components

```bash
satlinkbudget list transceivers
satlinkbudget list antennas
satlinkbudget list groundstations
```

### Run a single-point link budget

```bash
satlinkbudget budget missions/cubesat_uhf_downlink.yaml --elevation 30
```

### Run a full pass simulation with plots

```bash
satlinkbudget run missions/cubesat_uhf_downlink.yaml --plot --save-plots output/
```

---

## Next Steps

- **[Link Budget Walkthrough](link_budget_walkthrough.md)** — Expert-level step-by-step worked example with RF theory
- **[Standards References](standards_references.md)** — ITU-R, CCSDS, and ECSS standards implemented
- **[API Reference](api_reference.md)** — Complete module and function reference
- **[Component Database](component_database.md)** — Available transceivers, antennas, and ground stations
- **[Ecosystem Integration](ecosystem.md)** — Using satlinkbudget with sgp4, Skyfield, GNU Radio, and more
