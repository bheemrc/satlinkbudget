# Ecosystem Integration

satlinkbudget is designed to complement — not replace — the rich Python satellite ecosystem. This guide shows how to combine satlinkbudget's RF link analysis with orbit propagation, ephemeris, and signal processing tools.

---

## Package Comparison

| Capability | satlinkbudget | sgp4 | Skyfield | itur | pyorbital | GNU Radio |
|------------|:---:|:---:|:---:|:---:|:---:|:---:|
| Link budget computation | **Yes** | — | — | — | — | — |
| RF path loss models | **Yes** | — | — | — | — | — |
| ITU-R atmosphere models | **Yes** | — | — | **Yes** | — | — |
| Antenna gain models | **Yes** | — | — | — | — | — |
| Modulation / BER curves | **Yes** | — | — | — | — | **Yes** |
| TLE orbit propagation | Keplerian+J2 | **Yes (SGP4)** | **Yes** | — | **Yes** | — |
| High-precision ephemeris | — | — | **Yes (JPL)** | — | — | — |
| Contact window finding | **Yes** | — | **Yes** | — | **Yes** | — |
| Doppler computation | **Yes** | — | **Yes** | — | **Yes** | — |
| Pass simulation + report | **Yes** | — | — | — | — | — |
| SDR signal processing | — | — | — | — | — | **Yes** |
| Component database | **Yes** | — | — | — | — | — |

**Key insight:** satlinkbudget provides the RF link analysis layer that other packages don't cover. Use it with sgp4/Skyfield for orbit precision, itur for full ITU-R models, and GNU Radio for implementation.

---

## sgp4 — TLE-Based Orbit Propagation

The [sgp4](https://pypi.org/project/sgp4/) library implements the SGP4/SDP4 orbital propagation algorithm used by NORAD/CelesTrak. It provides higher-fidelity orbit prediction than satlinkbudget's Keplerian model, especially for non-circular orbits and long prediction horizons.

### Using the built-in adapter

```python
from satlinkbudget.contrib._sgp4 import orbit_from_tle

# ISS TLE (update from CelesTrak for current epoch)
line1 = "1 25544U 98067A   24001.50000000  .00016717  00000-0  10270-3 0  9006"
line2 = "2 25544  51.6400 300.0000 0006000  50.0000 310.0000 15.49560000400000"

orbit = orbit_from_tle(line1, line2)

# Compatible with find_contacts and PassSimulation
state = orbit.propagate(0.0)
print(f"Position: {state.position_eci / 1e3} km")
print(f"Period: {orbit.period_s / 60:.1f} min")
```

### Direct integration

```python
from sgp4.api import Satrec, WGS72
from satlinkbudget.rf import slant_range, free_space_path_loss_db

sat = Satrec.twoline2rv(line1, line2, WGS72)
e, r_km, v_km_s = sat.sgp4(sat.jdsatepoch, sat.jdsatepochF)

# Use SGP4 range with satlinkbudget RF math
distance_m = slant_range(420e3, 30.0)  # or compute from SGP4 positions
fspl = free_space_path_loss_db(distance_m, 437e6)
```

**Install:** `pip install satlinkbudget[sgp4]`

---

## Skyfield — High-Precision Ephemerides

[Skyfield](https://rhodesmill.org/skyfield/) provides sub-arcsecond precision using JPL ephemerides and full IAU coordinate transformations. Use it when you need:
- Sub-kilometer position accuracy
- Precise pass timing for scheduling
- Topocentric coordinates for antenna pointing

### Using the built-in adapter

```python
from skyfield.api import load, EarthSatellite
from satlinkbudget.contrib._skyfield import orbit_from_skyfield, ground_station_from_skyfield

ts = load.timescale()
line1 = "1 25544U 98067A   ..."
line2 = "2 25544  51.6400 ..."

satellite = EarthSatellite(line1, line2, "ISS", ts)
orbit = orbit_from_skyfield(satellite, ts)

# Use with satlinkbudget simulation
state = orbit.propagate(0.0)
```

### Ground station conversion

```python
from skyfield.api import Topos
from satlinkbudget.contrib._skyfield import ground_station_from_skyfield

topos = Topos(latitude_degrees=78.23, longitude_degrees=15.39, elevation_m=400)
gs = ground_station_from_skyfield("Svalbard", topos)
```

**Install:** `pip install satlinkbudget[skyfield]`

---

## itur (ITU-Rpy) — Full ITU-R Propagation Suite

The [itur](https://github.com/iportillo/ITU-Rpy) package implements the full ITU-R P-series with line-by-line P.676, rain climatology maps, and statistical models. Use it as a drop-in replacement for `compute_atmospheric_losses` when you need:
- Full P.676 Annex 1 (line-by-line) accuracy
- P.837 rain rate climatology maps (vs. providing your own rain rate)
- Statistical availability calculations (0.01% to 50% of time)

### Drop-in usage

```python
import itur

# Full ITU-R atmospheric losses with climatological data
atm_loss = float(itur.atmospheric_attenuation_slant_path(
    lat=52, lon=10,
    f=437,          # MHz → itur uses GHz, check unit convention
    el=30,
    p=1,            # percentage of time
))

# Use in satlinkbudget link budget
from satlinkbudget.budget import compute_link_budget

result = compute_link_budget(
    transmitter=tx,
    receiver=rx,
    frequency_hz=437e6,
    distance_m=distance_m,
    data_rate_bps=9600,
    required_eb_n0_db=5.6,
    atmospheric_loss_db=atm_loss,  # from itur
)
```

---

## GNU Radio — SDR Signal Processing

[GNU Radio](https://www.gnuradio.org/) is the standard open-source SDR framework. Use satlinkbudget to **design** the link, then GNU Radio to **implement** the modem:

1. **Link budget analysis** with satlinkbudget → determines required Eb/N₀, data rate, Doppler range
2. **Signal processing chain** in GNU Radio → implements modulation, coding, synchronization
3. **Doppler prediction** from satlinkbudget pass simulation → drives GNU Radio frequency correction

```python
# satlinkbudget: determine link parameters
from satlinkbudget.budget import compute_max_data_rate
from satlinkbudget.orbit import max_doppler_shift

max_rate = compute_max_data_rate(tx, rx, 437e6, slant_range(500e3, 10.0), 5.6)
max_doppler = max_doppler_shift(500e3, 437e6)

print(f"Design data rate: {max_rate:.0f} bps")
print(f"Doppler range: ±{max_doppler:.0f} Hz → receiver bandwidth must accommodate")
```

---

## pyorbital — TLE Downloading from CelesTrak

[pyorbital](https://github.com/pytroll/pyorbital) provides TLE downloading from CelesTrak and basic orbit propagation:

```python
from pyorbital.orbital import Orbital

orb = Orbital("ISS (ZARYA)")
# Get current TLE from CelesTrak
line1, line2 = orb.tle._line1, orb.tle._line2

# Feed into satlinkbudget SGP4 adapter
from satlinkbudget.contrib._sgp4 import orbit_from_tle
orbit = orbit_from_tle(line1, line2)
```

---

## Typical Workflow

For a complete mission analysis workflow:

```
1. Download TLE          → pyorbital / CelesTrak API
2. Propagate orbit       → sgp4 or Skyfield (via contrib adapter)
3. Find contact windows  → satlinkbudget.orbit.find_contacts()
4. Atmospheric losses    → satlinkbudget.atmosphere or itur
5. Link budget per step  → satlinkbudget.budget.compute_link_budget()
6. Data volume estimate  → satlinkbudget.simulation.PassSimulation
7. Design modem chain    → satlinkbudget.modem → GNU Radio
```
