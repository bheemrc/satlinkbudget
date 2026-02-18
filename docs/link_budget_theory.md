# Link Budget Theory

This document describes the RF link budget equation and the models implemented in satlinkbudget.

## The Link Budget Equation

The fundamental link budget equation computes the carrier-to-noise-density ratio:

```
C/N₀ [dB·Hz] = EIRP + G/T - FSPL - L_atm - L_misc - k_B
```

Where:
- **EIRP** = Effective Isotropic Radiated Power [dBW] = P_tx + G_tx - L_feed - L_pointing
- **G/T** = Receiver figure of merit [dB/K] = G_rx - 10·log₁₀(T_sys)
- **FSPL** = Free-Space Path Loss [dB] = 20·log₁₀(4πdf/c)
- **L_atm** = Atmospheric losses [dB] (gaseous + rain + cloud + scintillation)
- **L_misc** = Miscellaneous losses [dB] (polarization mismatch, implementation)
- **k_B** = Boltzmann constant = -228.6 dBW/K/Hz

The energy-per-bit to noise-density ratio is:

```
Eb/N₀ [dB] = C/N₀ - 10·log₁₀(R_bit)
```

The **link margin** is:

```
Margin [dB] = Eb/N₀_received - Eb/N₀_required
```

A positive margin means the link closes.

## Free-Space Path Loss

```
FSPL = 20·log₁₀(4πdf/c)
```

Where d is the slant range from ground station to satellite:

```
R = √((R_E + h)² - R_E²·cos²(El)) - R_E·sin(El)
```

With R_E = 6,371 km (Earth radius), h = orbit altitude, El = elevation angle.

## System Noise Temperature

The Friis formula for cascaded noise:

```
T_sys = T_ant + T_LNA + T_sub / G_LNA
```

Noise figure to temperature conversion:

```
T = T_ref · (10^(NF/10) - 1)
```

where T_ref = 290 K.

## Atmospheric Models

### ITU-R P.676: Gaseous Absorption

Oxygen and water vapor absorption lines. Dominant effects:
- O₂ resonance complex at 60 GHz (~15 dB/km)
- O₂ line at 118.75 GHz
- H₂O line at 22.235 GHz
- H₂O line at 183.31 GHz

Slant path attenuation uses the equivalent height model:

```
A_gas = (γ_o · h_o + γ_w · h_w) / sin(El)
```

### ITU-R P.618 / P.838: Rain Attenuation

Specific attenuation from P.838 regression coefficients:

```
γ_R = k · R^α  [dB/km]
```

Where k and α depend on frequency, elevation, and polarization tilt. The full P.618 procedure applies effective path length reduction for the percentage of time exceeded.

### ITU-R P.840: Cloud and Fog

Rayleigh approximation for small water droplets:

```
A_cloud = K_l · LWC / sin(El)
```

### ITU-R P.531: Ionospheric Scintillation

Amplitude scintillation characterized by the S₄ index, inversely proportional to f^1.5. Significant below ~4 GHz, especially at low elevation near the geomagnetic equator.

## Antenna Models

### Parabolic Dish

```
G = η · (πDf/c)²
BW_3dB = 21° / (f_GHz · D_m)
```

Typical efficiencies: 0.55-0.65 for Cassegrain, 0.50-0.55 for prime focus.

### Patch Array

```
G_array = G_element + 10·log₁₀(N)
```

Where N is the number of elements (assumes ideal combining).

### Axial-Mode Helix (Kraus)

```
G = 10.8 + 10·log₁₀(N · S · C² / λ³)
```

Where N = turns, S = spacing, C = circumference.

### Pointing Loss

```
L_point = 12 · (θ_off / BW_3dB)² [dB]
```

### Polarization Mismatch

- Co-polarized: 0 dB
- Cross-polarized linear: ∞ dB (total)
- Linear to circular: 3 dB
- RHCP to LHCP: ∞ dB (total)

## Modulation & Coding

### BER Curves

| Scheme | BER Formula | Eb/N₀ at BER=10⁻⁵ |
|--------|-------------|-------------------|
| BPSK | Q(√(2·Eb/N₀)) | 9.6 dB |
| QPSK | Q(√(2·Eb/N₀)) | 9.6 dB |
| 8PSK | (2/3)·erfc(√(3·Eb/N₀)·sin(π/8)) | ~13 dB |
| 16QAM | (3/8)·erfc(√(2·Eb/N₀/5)) | ~14 dB |

### FEC Coding Gains

| Code | Rate | Coding Gain |
|------|------|-------------|
| Uncoded | 1.0 | 0.0 dB |
| Convolutional R=1/2, K=7 | 0.5 | 5.0 dB |
| Turbo R=1/2 | 0.5 | 8.0 dB |
| LDPC R=1/2 | 0.5 | 7.5 dB |
| LDPC R=3/4 | 0.75 | 6.0 dB |
| LDPC R=7/8 | 0.875 | 4.5 dB |

## Orbit Mechanics

### Keplerian Period

```
T = 2π · √(a³/μ)
```

For a 500 km circular orbit: T ≈ 5670 s (94.5 min).

### J2 Secular Perturbation

The oblateness of Earth causes secular drift in RAAN and argument of perigee:

```
Ω̇ = -1.5 · n · J₂ · (R_E/a)² · cos(i)
ω̇ = 0.75 · n · J₂ · (R_E/a)² · (5·cos²(i) - 1)
```

Sun-synchronous orbits use this RAAN drift to maintain a constant local solar time.

### Doppler Shift

```
Δf = f · v_r / c
```

Maximum Doppler occurs at horizon crossing. For 500 km altitude at UHF (437 MHz): Δf_max ≈ ±10 kHz.
