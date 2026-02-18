# API Reference

## Core API Functions

### `run_link_budget(request) → LinkBudgetResponse`

Compute a single-point link budget.

```python
from satlinkbudget.api import run_link_budget
from satlinkbudget.api._schemas import LinkBudgetRequest

req = LinkBudgetRequest(
    tx_power_dbm=33.0,
    tx_antenna_gain_dbi=5.15,
    rx_antenna_gain_dbi=14.0,
    rx_system_noise_temp_k=500.0,
    frequency_hz=437e6,
    distance_m=1200e3,
    data_rate_bps=9600,
    modulation="BPSK",
    coding="convolutional_r12",
)

resp = run_link_budget(req)
# resp.margin_db, resp.link_closes, resp.eirp_dbw, resp.eb_n0_db, ...
```

**Request fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `tx_power_dbm` | float | required | Transmitter power [dBm] |
| `tx_antenna_gain_dbi` | float | required | Tx antenna gain [dBi] |
| `tx_feed_loss_db` | float | 0.0 | Tx feed/cable loss [dB] |
| `tx_pointing_loss_db` | float | 0.0 | Tx pointing loss [dB] |
| `rx_antenna_gain_dbi` | float | required | Rx antenna gain [dBi] |
| `rx_system_noise_temp_k` | float | required | System noise temp [K] |
| `rx_feed_loss_db` | float | 0.0 | Rx feed/cable loss [dB] |
| `frequency_hz` | float | required | Carrier frequency [Hz] |
| `distance_m` | float | required | Link distance [m] |
| `data_rate_bps` | float | required | Data rate [bps] |
| `modulation` | str | "BPSK" | BPSK, QPSK, 8PSK, 16QAM |
| `coding` | str | "uncoded" | uncoded, convolutional_r12, turbo_r12, ldpc_r12, ldpc_r34, ldpc_r78 |
| `implementation_loss_db` | float | 1.0 | Modem implementation loss [dB] |
| `atmospheric_loss_db` | float | 0.0 | Total atmospheric loss [dB] |
| `polarization_loss_db` | float | 0.0 | Polarization mismatch loss [dB] |

**Response fields:**

| Field | Type | Description |
|-------|------|-------------|
| `eirp_dbw` | float | Effective Isotropic Radiated Power [dBW] |
| `figure_of_merit_db_per_k` | float | Receiver G/T [dB/K] |
| `free_space_path_loss_db` | float | FSPL [dB] |
| `c_over_n0_db_hz` | float | Carrier-to-noise density [dB·Hz] |
| `eb_n0_db` | float | Received Eb/N₀ [dB] |
| `required_eb_n0_db` | float | Required Eb/N₀ for target BER [dB] |
| `margin_db` | float | Link margin [dB] |
| `link_closes` | bool | True if margin > 0 |
| `text_report` | str | Formatted text report |

---

### `run_pass_simulation(request) → PassSimulationResponse`

Run a multi-orbit pass simulation over a ground station.

```python
from satlinkbudget.api import run_pass_simulation
from satlinkbudget.api._schemas import PassSimulationRequest

req = PassSimulationRequest(
    mission_preset="cubesat_uhf_downlink",
    duration_orbits=24,
    dt_s=1.0,
)

resp = run_pass_simulation(req)
# resp.num_passes, resp.total_data_volume_mbytes, resp.text_report, ...
```

**Request fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `mission_yaml` | str | "" | YAML config string (inline) |
| `mission_preset` | str | "" | Preset mission name |
| `duration_orbits` | float | 24.0 | Simulation duration in orbits |
| `dt_s` | float | 1.0 | Time step [s] |

Provide either `mission_yaml` or `mission_preset` (not both).

**Response fields:**

| Field | Type | Description |
|-------|------|-------------|
| `num_passes` | int | Number of contact passes |
| `total_contact_time_s` | float | Total contact time [s] |
| `passes_per_day` | float | Average passes per day |
| `total_data_volume_bits` | float | Total data transferred [bits] |
| `total_data_volume_mbytes` | float | Total data transferred [MB] |
| `avg_pass_duration_s` | float | Average pass duration [s] |
| `text_report` | str | Formatted text report |

---

### `list_components(category) → list[str]`

List available components in a category.

```python
from satlinkbudget.api import list_components

transceivers = list_components("transceivers")
antennas = list_components("antennas")
groundstations = list_components("groundstations")
bands = list_components("bands")
missions = list_components("missions")
```

---

### `get_component(category, name) → dict`

Get details for a specific component.

```python
from satlinkbudget.api import get_component

radio = get_component("transceivers", "endurosat_uhf_transceiver_ii")
```

---

## RF Module

### Conversions

```python
from satlinkbudget.rf import (
    to_db, from_db,
    watts_to_dbw, dbw_to_watts,
    watts_to_dbm, dbm_to_watts,
    frequency_to_wavelength, wavelength_to_frequency,
)

to_db(100)          # 20.0
watts_to_dbm(2.0)   # 33.01 dBm
frequency_to_wavelength(437e6)  # 0.686 m
```

### Path Loss

```python
from satlinkbudget.rf import free_space_path_loss_db, slant_range

fspl = free_space_path_loss_db(distance_m=1200e3, frequency_hz=437e6)
dist = slant_range(altitude_m=500e3, elevation_deg=30.0)
```

### Noise

```python
from satlinkbudget.rf import (
    system_noise_temperature,
    noise_figure_to_temperature,
    figure_of_merit_db,
    antenna_noise_temperature,
    rain_noise_temperature,
)

t_sys = system_noise_temperature(t_ant=150.0, t_lna=35.0, g_lna_db=30.0, t_subsequent=1000.0)
t_nf = noise_figure_to_temperature(nf_db=0.8)
```

---

## Atmospheric Models

```python
from satlinkbudget.atmosphere import compute_atmospheric_losses

losses = compute_atmospheric_losses(
    freq_ghz=0.437,
    elevation_deg=30.0,
    rain_rate_mm_hr=10.0,
    cloud_lwc_kg_m2=0.5,
)

print(f"Gaseous: {losses.gaseous_db:.2f} dB")
print(f"Rain: {losses.rain_db:.2f} dB")
print(f"Cloud: {losses.cloud_db:.2f} dB")
print(f"Scintillation: {losses.scintillation_db:.2f} dB")
print(f"Total: {losses.total_db:.2f} dB")
```

---

## Antenna Models

```python
from satlinkbudget.antenna import (
    ParabolicAntenna,
    PatchAntenna,
    HelixAntenna,
    DipoleAntenna,
    MonopoleAntenna,
    HornAntenna,
    pointing_loss_db,
    polarization_mismatch_loss_db,
)

dish = ParabolicAntenna(diameter_m=3.7, efficiency=0.6)
dish.gain_db(8.2e9)       # ~47 dBi
dish.beamwidth_deg(8.2e9) # ~0.69°

helix = HelixAntenna(num_turns=10, circumference_m=0.7, spacing_m=0.17)
helix.gain_db(437e6)

loss = pointing_loss_db(off_axis_deg=2.0, bw_3db_deg=10.0)
pol_loss = polarization_mismatch_loss_db("linear", "circular")  # 3.0 dB
```

---

## Budget Engine

```python
from satlinkbudget.budget import (
    TransmitterChain,
    ReceiverChain,
    compute_link_budget,
    compute_max_data_rate,
    compute_required_power_dbw,
)

tx = TransmitterChain.from_power_dbm(33.0, antenna_gain_dbi=5.15)
rx = ReceiverChain(antenna_gain_dbi=14.0, system_noise_temp_k=500.0)

result = compute_link_budget(
    transmitter=tx,
    receiver=rx,
    frequency_hz=437e6,
    distance_m=1200e3,
    data_rate_bps=9600,
    required_eb_n0_db=5.6,
)

print(result.to_text())
fig = result.plot_waterfall()
```

---

## Orbit & Contacts

```python
from satlinkbudget.orbit import (
    Orbit,
    GroundStation,
    find_contacts,
    doppler_shift,
    max_doppler_shift,
)

orbit = Orbit.circular(altitude_km=500, inclination_deg=97.4)
gs = GroundStation(name="Svalbard", latitude_deg=78.23, longitude_deg=15.39, altitude_m=400.0)

contacts = find_contacts(orbit, gs, duration_s=86400, dt_s=10.0)
print(f"Passes: {contacts.num_contacts}")

for window in contacts.windows:
    print(f"  {window.duration_s:.0f}s, max el: {window.max_elevation_deg:.1f}°")
```
