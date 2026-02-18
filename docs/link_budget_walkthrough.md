# Link Budget Walkthrough

A step-by-step worked example of a complete RF link budget for a 3U CubeSat UHF downlink, explaining every term, every sign convention, and every standard referenced.

> **Note:** Numerical results in this walkthrough are based on analytical models and textbook parameters. They are intended for educational and preliminary design purposes. Actual mission link budgets require measured hardware parameters, site-specific atmospheric data, and independent verification.

---

## What Is a Link Budget?

A link budget is a line-item accounting of every gain, loss, and noise contribution between a transmitter and receiver in a radio communication system. For small satellites, the link budget answers the critical question: **will the ground station receive telemetry with enough signal-to-noise ratio to decode data reliably?**

Unlike terrestrial systems where you can increase power or add repeaters, spacecraft links are constrained by strict power budgets (watts), antenna size (volume-limited CubeSats), and enormous path distances (hundreds to thousands of kilometers). The link budget quantifies whether the system closes — that is, whether the received signal exceeds the minimum required for acceptable bit error performance — and by how much margin.

The margin must account for uncertainties: hardware tolerances, atmospheric variability, pointing jitter, and thermal effects. A well-designed LEO CubeSat link targets 3–6 dB of margin for reliable operations.

---

## The Complete Link Budget Equation

```
C/N₀ = EIRP + G/T − FSPL − L_atm − L_pol − L_misc − k_B    [dB·Hz]

Eb/N₀ = C/N₀ − 10·log₁₀(R_b)                                [dB]

Margin = Eb/N₀_received − Eb/N₀_required                      [dB]
```

Every term is in decibels. Gains are positive; losses are positive numbers that are *subtracted*.

---

## Worked Example: 3U CubeSat UHF Downlink

**Scenario:** A 3U CubeSat at 500 km altitude in a Sun-synchronous orbit downlinks housekeeping telemetry at 9600 bps using BPSK + convolutional coding (R=1/2, K=7) to a SatNOGS ground station. We compute the link at 30° elevation.

### Step 1: Transmitter Chain → EIRP

The Effective Isotropic Radiated Power combines the transmitter power, antenna gain, and all losses before radiation:

```
EIRP = P_tx + G_tx − L_feed − L_pointing    [dBW]
```

| Parameter | Value | Notes |
|-----------|-------|-------|
| P_tx | 33 dBm = **3.0 dBW** | Endurosat UHF II, 2W RF output |
| G_tx | **5.15 dBi** | Quarter-wave monopole over ground plane |
| L_feed | **0.5 dB** | Coax + connectors (short run on CubeSat) |
| L_pointing | **1.0 dB** | 5° pointing error, 45° beamwidth, L = 12·(θ/BW)² |

**dBm to dBW conversion:** P[dBW] = P[dBm] − 30. So 33 dBm = 3 dBW.

```
EIRP = 3.0 + 5.15 − 0.5 − 1.0 = +6.65 dBW
```

In satlinkbudget:

```python
from satlinkbudget.budget import TransmitterChain

tx = TransmitterChain.from_power_dbm(
    power_dbm=33.0,
    antenna_gain_dbi=5.15,
    feed_loss_db=0.5,
    pointing_loss_db=1.0,
)
print(f"EIRP: {tx.eirp_dbw:+.2f} dBW")   # +6.65 dBW
```

### Step 2: Slant Range Geometry + Free-Space Path Loss

The slant range from ground station to satellite depends on altitude and elevation angle. Using spherical Earth geometry:

```
R = −R_E·sin(El) + √((R_E·sin(El))² + r_sat² − R_E²)
```

Where R_E = 6,378,137 m, r_sat = R_E + h = 6,378,137 + 500,000 = 6,878,137 m, and El = 30°.

This gives **R ≈ 909.5 km** at 30° elevation. Compare with the zenith case (90°): R = h = 500 km. At the horizon (0°): R ≈ 2,294 km.

The free-space path loss (FSPL) follows from the Friis transmission equation:

```
FSPL = 20·log₁₀(4π·d·f/c)    [dB]
```

At d = 909,500 m, f = 437 MHz:

```
FSPL = 20·log₁₀(4π × 909500 × 437×10⁶ / 299792458) = 144.43 dB
```

```python
from satlinkbudget.rf import slant_range, free_space_path_loss_db

d = slant_range(500e3, 30.0)     # 909,500 m
fspl = free_space_path_loss_db(d, 437e6)  # 144.43 dB
```

### Step 3: Atmospheric Losses

Atmospheric propagation losses come from four mechanisms, each modeled by an ITU-R Recommendation:

| Loss Component | ITU-R Standard | Contribution at UHF, 30° | Notes |
|---------------|---------------|--------------------------|-------|
| Gaseous absorption | P.676-13 | ~0.05 dB | O₂ + H₂O; negligible at UHF |
| Rain attenuation | P.618-14 / P.838-3 | ~0 dB | No rain assumed for clear-sky design |
| Cloud/fog | P.840-8 | ~0 dB | Negligible at UHF |
| Scintillation | P.531-14 | ~0.3–1.0 dB | Ionospheric; can matter at UHF |

For this example, we use a conservative total of **0.5 dB**.

At higher frequencies (X-band, Ka-band), atmospheric losses become dominant. See the [atmospheric effects plots](images/atmospheric_vs_frequency.png) for frequency dependence.

```python
from satlinkbudget.atmosphere import compute_atmospheric_losses

losses = compute_atmospheric_losses(
    freq_ghz=0.437,
    elevation_deg=30.0,
    rain_rate_001_mm_h=0.0,
)
print(f"Total atmospheric loss: {losses.total_db:.2f} dB")
```

### Step 4: Receiver Chain → G/T

The receiver figure of merit G/T combines antenna gain and system noise temperature:

```
G/T = G_rx − L_feed − L_pointing − 10·log₁₀(T_sys)    [dB/K]
```

The system noise temperature follows the Friis cascaded noise formula:

```
T_sys = T_ant + T_LNA + T_subsequent / G_LNA
```

For a warm ground station at UHF (sky + ground noise ≈ 200 K, LNA noise figure 0.8 dB):

| Parameter | Value | Notes |
|-----------|-------|-------|
| G_rx | **14.0 dBi** | 10-element UHF Yagi |
| L_feed | **0.3 dB** | Short cable to LNA |
| T_sys | **500 K** | Conservative (includes sky, ground spillover, LNA) |

```
G/T = 14.0 − 0.3 − 10·log₁₀(500) = 14.0 − 0.3 − 27.0 = −13.29 dB/K
```

```python
from satlinkbudget.budget import ReceiverChain

rx = ReceiverChain(
    antenna_gain_dbi=14.0,
    system_noise_temp_k=500.0,
    feed_loss_db=0.3,
)
print(f"G/T: {rx.figure_of_merit_db_per_k:+.2f} dB/K")  # -13.29 dB/K
```

### Step 5: C/N₀ Assembly

Carrier-to-noise-density ratio — the central figure:

```
C/N₀ = EIRP + G/T − FSPL − L_atm − L_pol − L_misc − k_B
```

Where k_B = −228.6 dBW/K/Hz (Boltzmann constant). Subtracting a negative constant *adds* to the link budget.

| Line Item | Value [dB] | Running Total |
|-----------|-----------|---------------|
| EIRP | +6.65 | +6.65 |
| G/T | −13.29 | −6.64 |
| FSPL | −144.43 | −151.07 |
| Atmospheric | −0.50 | −151.57 |
| Polarization | 0.00 | −151.57 |
| −k_B | +228.60 | **+77.03** |

**C/N₀ = 77.03 dB·Hz**

### Step 6: Eb/N₀ and Link Margin

Convert C/N₀ to energy-per-bit:

```
Eb/N₀ = C/N₀ − 10·log₁₀(R_b) = 77.03 − 10·log₁₀(9600) = 77.03 − 39.82 = 37.20 dB
```

The required Eb/N₀ depends on modulation and coding:

- BPSK uncoded at BER = 10⁻⁵: ~9.6 dB
- Convolutional R=1/2, K=7 coding gain: ~5.0 dB
- Implementation loss: 1.0 dB
- **Required Eb/N₀ = 9.6 − 5.0 + 1.0 = 5.6 dB**

```
Margin = 37.20 − 5.59 = +31.62 dB    ✓ Link CLOSES
```

This generous margin is typical for UHF CubeSat links at moderate elevation — the low frequency and wide beamwidths work strongly in favor of closing the link. The margin would be lower at:
- Lower elevation (longer path, more atmospheric loss)
- Higher data rates (less energy per bit)
- Higher frequencies (more FSPL)

### Step 7: Time-Varying Analysis Over a Pass

During a real satellite pass, elevation changes continuously from horizon to maximum and back. This means FSPL, atmospheric losses, and Doppler shift all vary with time.

satlinkbudget's `PassSimulation` engine computes the link budget at every time step:

1. Propagate orbit to get satellite position
2. Compute elevation angle and slant range
3. Compute elevation-dependent atmospheric losses
4. Run the full link budget
5. Compute Doppler shift for frequency tracking

The result is time series of margin, C/N₀, and data volume — see the [pass simulation plots](images/pass_margin.png).

At low elevation angles (near horizon):
- Slant range is maximum → higher FSPL
- Atmospheric path is longest → higher attenuation
- Margin is minimum → link may not close below ~5–10° elevation

This is why ground stations define a minimum elevation angle (typically 5–10°), and why the pass simulation is essential for realistic link performance assessment.

---

## Summary Table

| Parameter | Symbol | Value | Unit |
|-----------|--------|-------|------|
| TX Power | P_tx | +3.00 | dBW |
| TX Antenna Gain | G_tx | +5.15 | dBi |
| TX Losses | L_tx | −1.50 | dB |
| **EIRP** | | **+6.65** | **dBW** |
| Frequency | f | 437 | MHz |
| Slant Range | d | 909.5 | km |
| **FSPL** | | **−144.43** | **dB** |
| Atmospheric Loss | L_atm | −0.50 | dB |
| RX Antenna Gain | G_rx | +14.00 | dBi |
| RX Losses | L_rx | −0.30 | dB |
| System Noise Temp | T_sys | 500 | K |
| **G/T** | | **−13.29** | **dB/K** |
| Boltzmann | −k_B | +228.60 | dBW/K/Hz |
| **C/N₀** | | **+77.03** | **dB·Hz** |
| Data Rate | R_b | 9,600 | bps |
| **Eb/N₀ received** | | **+37.20** | **dB** |
| Eb/N₀ required | | +5.59 | dB |
| **Margin** | | **+31.62** | **dB** |

---

## Further Reading

- **[Link Budget Theory](link_budget_theory.md)** — Detailed formulas for all models
- **[Standards References](standards_references.md)** — ITU-R, CCSDS, ECSS implementation details
- **[Validation](validation.md)** — Cross-checks against reference values
- SMAD Chapter 13 — Communications Architecture (Wertz, Everett, Puschell)
- ITU-R P.676-13 — Gaseous absorption
- ITU-R P.618-14 / P.838-3 — Rain attenuation
- CCSDS 401.0-B — RF and Modulation Systems
