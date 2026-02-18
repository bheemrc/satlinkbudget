# Component Database

satlinkbudget ships with a curated database of satellite communication components stored as YAML datasheets. Components are discovered automatically at runtime via glob patterns.

## Transceivers

| Name | Band | Frequency | Tx Power | Data Rate |
|------|------|-----------|----------|-----------|
| Endurosat UHF Transceiver II | UHF | 435-438 MHz | 33 dBm (2W) | Up to 19.2 kbps |
| NanoAvionics UHF | UHF | 435-438 MHz | 30 dBm (1W) | Up to 9.6 kbps |
| AAC Clyde VUTRX | VHF/UHF | 144-146 / 435-438 MHz | 30 dBm (1W) | Up to 9.6 kbps |
| ISIS TXS S-band | S-band | 2200-2290 MHz | 33 dBm (2W) | Up to 1 Mbps |
| Syrlinks EWC27 X-band | X-band | 8025-8400 MHz | 37 dBm (5W) | Up to 100 Mbps |

## Antennas

| Name | Type | Gain | Beamwidth | Use Case |
|------|------|------|-----------|----------|
| Monopole UHF QW | Monopole | 5.15 dBi | Omnidirectional | Satellite UHF |
| Helix UHF | Axial helix | ~12 dBi | ~35° | Satellite UHF |
| Yagi VHF 5-element | Yagi-Uda | ~10 dBi | ~40° | Ground VHF |
| Yagi UHF 10-element | Yagi-Uda | ~14 dBi | ~25° | Ground UHF |
| Patch S-band 2x2 | Patch array | ~14 dBi | ~30° | Satellite S-band |
| Horn X-band | Horn | ~20 dBi | ~15° | Satellite X-band |
| Parabolic 2.4m | Parabolic dish | 30-45 dBi | Freq-dependent | Ground station |
| Parabolic 3.7m | Parabolic dish | 34-48 dBi | Freq-dependent | Ground station |
| Parabolic 7.3m | Parabolic dish | 40-54 dBi | Freq-dependent | Ground station |
| Parabolic 13m | Parabolic dish | 45-60 dBi | Freq-dependent | Ground station / DSN |

## Ground Stations

| Name | Location | Latitude | Longitude | Antenna | Min Elevation |
|------|----------|----------|-----------|---------|---------------|
| KSAT Svalbard | Longyearbyen, Norway | 78.23°N | 15.39°E | 3.7m parabolic | 5° |
| KSAT TrollSat | Troll, Antarctica | 72.01°S | 2.53°E | 3.7m parabolic | 5° |
| NASA DSN Goldstone | California, USA | 35.43°N | 243.11°E | 13m / 34m / 70m | 6° |
| NASA DSN Canberra | ACT, Australia | 35.40°S | 148.98°E | 13m / 34m / 70m | 6° |
| NASA DSN Madrid | Robledo, Spain | 40.43°N | 355.75°E | 13m / 34m / 70m | 6° |
| ESA Kiruna | Kiruna, Sweden | 67.86°N | 20.96°E | 3.7m parabolic | 5° |
| ESA Kourou | French Guiana | 5.25°N | 307.19°E | 3.7m parabolic | 5° |
| SatNOGS Generic UHF | Generic mid-latitude | 45.0°N | 10.0°E | Yagi 14 dBi | 10° |
| Generic S-band 3.7m | Generic mid-latitude | 45.0°N | 10.0°E | 3.7m parabolic | 5° |

## Frequency Bands

| Band | Uplink Range | Downlink Range | Typical Use |
|------|-------------|----------------|-------------|
| VHF | 145.8-146.0 MHz | 145.8-146.0 MHz | Amateur satellite |
| UHF | 435-438 MHz | 435-438 MHz | CubeSat TT&C |
| S-band | 2025-2110 MHz | 2200-2290 MHz | LEO data downlink |
| X-band | 7145-7190 MHz | 8025-8400 MHz | EO data downlink |
| Ku-band | 14.0-14.5 GHz | 10.7-12.75 GHz | Fixed satellite |
| Ka-band | 27.5-30.0 GHz | 17.7-21.2 GHz | High throughput |
| Optical | — | 1550 nm | Laser comm (experimental) |

## Mission Presets

| Preset | Band | Orbit | Data Rate | Ground Station |
|--------|------|-------|-----------|----------------|
| `cubesat_uhf_downlink` | UHF 437 MHz | 500 km SSO | 9.6 kbps | SatNOGS generic |
| `cubesat_s_band_downlink` | S-band 2.25 GHz | 550 km SSO | 256 kbps | Generic S-band 3.7m |
| `eo_x_band_downlink` | X-band 8.2 GHz | 600 km SSO | 50 Mbps | KSAT Svalbard |
| `iot_uhf_uplink` | UHF 437 MHz | 500 km SSO | 1200 bps | SatNOGS generic |
| `deep_space_x_band` | X-band 8.4 GHz | Lunar distance | 64 kbps | DSN Goldstone |

## Adding Custom Components

Create a YAML file in the appropriate subdirectory under `src/satlinkbudget/data/`:

```yaml
# src/satlinkbudget/data/transceivers/my_radio.yaml
name: "My Custom Radio"
manufacturer: "Custom"
frequency_min_hz: 435.0e6
frequency_max_hz: 438.0e6
tx_power_dbm: 30.0
rx_sensitivity_dbm: -120.0
data_rates_bps: [1200, 9600]
mass_kg: 0.05
power_consumption_w: 2.0
```

The component will be automatically discovered by the registry on next import.
