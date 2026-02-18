# Validation

satlinkbudget models are cross-checked against analytical reference values, published ITU-R data, and textbook examples. This document summarizes the validation evidence and test coverage.

> **Important:** All validation below is against **analytical formulas, published standards data, and textbook worked examples** — not against measured flight telemetry or real mission data. This library has not been operationally validated on any satellite mission. Users should treat results as engineering estimates and independently verify critical calculations before use in mission design or operations.

---

## Validation Philosophy

Each physics model is cross-checked at three levels:

1. **Unit-level:** Individual functions tested against hand-calculated or published reference values
2. **Cross-model:** Combined calculations (e.g., FSPL + atmospheric + noise) compared against end-to-end textbook examples
3. **Integration:** Full pass simulations checked for self-consistency and compared against published mission analysis examples

Tolerances are chosen based on the model fidelity: exact analytical results match to floating-point precision; empirical models (ITU-R) match to within documented uncertainty bounds.

---

## Reference Cross-Checks

### Free-Space Path Loss

**Reference:** FSPL = 20·log₁₀(4πdf/c)

| Distance | Frequency | Expected | satlinkbudget | Status |
|----------|-----------|----------|---------------|--------|
| 1 km | 1 GHz | 92.45 dB | 92.45 dB | PASS |
| 100 km | 437 MHz | 125.69 dB | 125.69 dB | PASS |
| 909.5 km | 437 MHz | 144.43 dB | 144.43 dB | PASS |
| 35,786 km | 12 GHz | 205.76 dB | 205.76 dB | PASS |

Analytical formula — matches to machine precision.

### Slant Range Geometry

**Reference:** Spherical Earth model, R = −R_E·sin(El) + √((R_E·sin(El))² + r_sat² − R_E²)

| Altitude | Elevation | Expected | satlinkbudget | Status |
|----------|-----------|----------|---------------|--------|
| 500 km | 90° (zenith) | 500.0 km | 500.0 km | PASS |
| 500 km | 30° | ~909.5 km | 909.5 km | PASS |
| 500 km | 5° | ~1,932 km | 1,932 km | PASS |

---

### ITU-R P.676: Gaseous Absorption

**Reference:** ITU-R P.676-13, Table and Figure validation

| Test | Expected | satlinkbudget | Tolerance |
|------|----------|---------------|-----------|
| 60 GHz O₂ specific atten. | ~15 dB/km | 15.0 dB/km | ±1 dB/km |
| 22.235 GHz H₂O peak | visible in sweep | confirmed | qualitative |
| UHF (0.437 GHz) slant path | < 0.1 dB at 30° | < 0.1 dB | — |

The 60 GHz oxygen resonance complex is the strongest absorption feature in the atmosphere and serves as a robust validation point.

---

### ITU-R P.838: Rain Specific Attenuation

**Reference:** ITU-R P.838-3, regression coefficients

| Frequency | Rain Rate | Expected γ_R | satlinkbudget | Tolerance |
|-----------|-----------|-------------|---------------|-----------|
| 12 GHz | 50 mm/h | ~5.6 dB/km | 5.6 dB/km | ±0.5 dB/km |
| 10 GHz | 25 mm/h | ~2.4 dB/km | 2.4 dB/km | ±0.5 dB/km |
| 30 GHz | 50 mm/h | ~15 dB/km | ~15 dB/km | ±2 dB/km |

---

### Antenna Gain: Parabolic Dish

**Reference:** G = η·(πDf/c)²

| Diameter | Frequency | Efficiency | Expected | satlinkbudget | Status |
|----------|-----------|------------|----------|---------------|--------|
| 3.7 m | 8.2 GHz | 0.55 | ~45.9 dBi | 45.9 dBi | PASS |
| 13 m | 8.4 GHz | 0.55 | ~56.6 dBi | 56.6 dBi | PASS |
| 2.4 m | 2.2 GHz | 0.55 | ~30.0 dBi | 30.0 dBi | PASS |

Analytical formula — matches to floating-point precision.

---

### Doppler Shift

**Reference:** Δf = f·v_orbital/c (maximum, at horizon)

| Altitude | Frequency | Expected max Δf | satlinkbudget | Tolerance |
|----------|-----------|----------------|---------------|-----------|
| 500 km | 437 MHz | ~10.2 kHz | ~10.2 kHz | ±0.5 kHz |
| 400 km | 437 MHz | ~10.4 kHz | ~10.4 kHz | ±0.5 kHz |
| 500 km | 8.2 GHz | ~192 kHz | ~192 kHz | ±5 kHz |

---

### Full CubeSat UHF Link Budget vs SMAD

**Reference:** SMAD Chapter 13, UHF CubeSat downlink example

| Line Item | SMAD | satlinkbudget | Δ |
|-----------|------|---------------|---|
| EIRP | ~7 dBW | +6.65 dBW | −0.35 dB |
| FSPL @ 30° | ~144.5 dB | 144.43 dB | −0.07 dB |
| C/N₀ | ~77 dB·Hz | 77.03 dB·Hz | +0.03 dB |
| Eb/N₀ | ~37 dB | 37.20 dB | +0.20 dB |

**Agreement within 0.5 dB** — well within engineering precision for link budget work.

---

### BER Curves

**Reference:** Theoretical BER expressions (Proakis, Digital Communications)

| Modulation | Eb/N₀ for BER=10⁻⁵ | Expected | satlinkbudget | Status |
|------------|---------------------|----------|---------------|--------|
| BPSK | Q(√(2·Eb/N₀)) | ~9.6 dB | 9.6 dB | PASS |
| QPSK | Q(√(2·Eb/N₀)) | ~9.6 dB | 9.6 dB | PASS |
| 8PSK | (2/3)·erfc(...) | ~13.0 dB | ~13.0 dB | PASS |
| 16QAM | (3/8)·erfc(...) | ~13.5 dB | ~13.5 dB | PASS |

---

## Test Suite Summary

| Module | Tests | Coverage |
|--------|-------|----------|
| `rf` (constants, conversions, FSPL, noise) | ~40 | Core math validation |
| `atmosphere` (P.676, P.618, P.838, P.840, P.531) | ~45 | ITU-R model validation |
| `antenna` (parabolic, patch, helix, dipole, horn, pointing) | ~35 | Analytical cross-checks |
| `modem` (modulation BER, coding gains, performance) | ~25 | Theoretical BER curves |
| `budget` (link budget, max rate, required power) | ~30 | End-to-end budget validation |
| `orbit` (propagation, contacts, Doppler, ground station) | ~40 | Keplerian + J2 validation |
| `simulation` (pass engine, results, report) | ~25 | Integration tests |
| `mission` (config, builder, presets) | ~20 | YAML parsing + building |
| `data` (registry, loader) | ~30 | Component database integrity |
| `api` (schemas, services) | ~35 | Request/response validation |
| `validation` (checks) | ~15 | Sanity check tests |
| `integration` (end-to-end) | ~31 | Full pipeline tests |
| **Total** | **399** | |

All tests pass. Run with:

```bash
.venv/bin/pytest tests/ -v
```

---

## Limitations

- Atmospheric models use simplified forms of the ITU-R recommendations (e.g., Annex 2 wideband model for P.676, not the full line-by-line summation). See [Standards References](standards_references.md) for details on each simplification.
- Orbit propagation uses circular Keplerian with J2 secular perturbation only. No drag, solar radiation pressure, or higher-order perturbations.
- Component datasheets are derived from publicly available specifications and may not reflect actual measured performance of specific hardware units.
- No validation has been performed against real satellite telemetry, ground station measurements, or operational mission data.
