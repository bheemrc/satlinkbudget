# satlinkbudget

Aerospace-grade satellite link budget analysis library for Python.

Implements the complete RF link budget equation coupled with orbit propagation for time-varying link analysis over satellite passes:

```
C/N₀ = EIRP + G/T - FSPL - L_atm - L_misc - k_B
```

## Features

- **RF fundamentals** — free-space path loss, slant range, system noise temperature, G/T figure of merit
- **ITU-R atmospheric models** — P.676 gaseous absorption, P.618/P.838 rain attenuation, P.840 cloud/fog, P.531 ionospheric scintillation
- **Antenna models** — parabolic dish, patch array, axial-mode helix, dipole/monopole, horn, pointing loss, polarization mismatch
- **Modulation & coding** — BPSK, QPSK, 8PSK, 16QAM BER curves with convolutional, turbo, and LDPC FEC coding
- **Link budget engine** — full line-item C/N₀ → Eb/N₀ → margin calculation, max data rate solver, required power solver
- **Orbit propagation** — circular Keplerian with J2 secular perturbation, ground station contact windows, Doppler shift
- **Pass simulation** — time-stepping link budget over satellite passes with elevation-dependent range, atmospheric losses, and data volume tracking
- **Component database** — 31 YAML datasheets covering transceivers, antennas, ground stations, and frequency bands
- **Mission presets** — 5 ready-to-use mission configurations (CubeSat UHF/S-band, EO X-band, IoT uplink, deep space)
- **CLI and API** — command-line interface for quick analysis, Pydantic-based API for integration

## Installation

```bash
pip install -e .
```

Requires Python 3.11+. Dependencies: NumPy, SciPy, Pydantic, PyYAML, Matplotlib.

## Quick Start

### Python API

```python
from satlinkbudget.api import run_link_budget
from satlinkbudget.api._schemas import LinkBudgetRequest
from satlinkbudget.rf import slant_range

# UHF CubeSat downlink at 30° elevation
req = LinkBudgetRequest(
    tx_power_dbm=33.0,              # 2W transmitter
    tx_antenna_gain_dbi=5.15,        # quarter-wave monopole
    tx_pointing_loss_db=1.0,
    rx_antenna_gain_dbi=14.0,        # UHF Yagi ground antenna
    rx_system_noise_temp_k=500.0,
    frequency_hz=437e6,
    distance_m=slant_range(500e3, 30.0),
    data_rate_bps=9600,
    modulation="BPSK",
    coding="convolutional_r12",
    atmospheric_loss_db=0.5,
)

result = run_link_budget(req)
print(f"Margin: {result.margin_db:.1f} dB — {'CLOSES' if result.link_closes else 'FAILS'}")
```

### Pass Simulation

```python
from satlinkbudget.api import run_pass_simulation
from satlinkbudget.api._schemas import PassSimulationRequest

req = PassSimulationRequest(
    mission_preset="cubesat_uhf_downlink",
    duration_orbits=24,
    dt_s=1.0,
)

result = run_pass_simulation(req)
print(f"Passes: {result.num_passes}")
print(f"Total contact time: {result.total_contact_time_s:.0f} s")
print(f"Data volume: {result.total_data_volume_mbytes:.2f} MB")
```

### CLI

```bash
# List available components
satlinkbudget list transceivers
satlinkbudget list antennas
satlinkbudget list groundstations

# Single link budget at 30° elevation
satlinkbudget budget missions/cubesat_uhf_downlink.yaml --elevation 30

# Full pass simulation with plots
satlinkbudget run missions/cubesat_uhf_downlink.yaml --plot --save-plots output/
```

## Architecture

```
src/satlinkbudget/
├── rf/              # Core RF math (FSPL, noise, conversions)
├── atmosphere/      # ITU-R atmospheric models (P.676, P.618, P.840, P.531)
├── antenna/         # Antenna gain models + pointing/polarization losses
├── modem/           # Modulation schemes + FEC coding
├── budget/          # Link budget engine (transmitter, receiver, margin)
├── orbit/           # Orbit propagation + ground station contacts + Doppler
├── simulation/      # Time-stepping pass simulation
├── mission/         # YAML mission config + builder
├── data/            # Component database (31 YAML datasheets)
├── api/             # Pydantic request/response API layer
└── validation/      # Compatibility and sanity checks
```

## Component Database

| Category | Count | Examples |
|---|---|---|
| Transceivers | 5 | Endurosat UHF II, ISIS TXS S-band, Syrlinks EWC27 X-band |
| Antennas | 10 | Parabolic 3.7m, Yagi UHF 10-element, Patch S-band 2x2, Helix UHF |
| Ground Stations | 9 | KSAT Svalbard, NASA DSN Goldstone/Canberra/Madrid, ESA Kiruna |
| Frequency Bands | 7 | VHF, UHF, S, X, Ku, Ka, Optical |
| Mission Presets | 5 | CubeSat UHF/S-band downlink, EO X-band, IoT uplink, Deep space |

## Mission Configuration

Missions are defined as YAML files combining orbit, transmitter, receiver, modem, and simulation parameters:

```yaml
name: "CubeSat UHF Downlink"
frequency_hz: 437.0e6

orbit:
  altitude_km: 500
  inclination_deg: 97.4

transmitter:
  transceiver: "endurosat_uhf_transceiver_ii"
  antenna: "monopole_uhf_qw"
  pointing_error_deg: 5.0

receiver:
  ground_station: "satnogs_generic_uhf"
  lna_noise_figure_db: 0.8

modem:
  modulation: "BPSK"
  coding: "convolutional_r12"
  data_rate_bps: 9600

simulation:
  duration_orbits: 24
  dt_s: 1.0
```

## Testing

```bash
# Full test suite (371 tests)
.venv/bin/pytest tests/ -v

# Specific module
.venv/bin/pytest tests/test_rf/ -v
.venv/bin/pytest tests/test_budget/ -v
```

## License

Apache 2.0. See [LICENSE](LICENSE).
