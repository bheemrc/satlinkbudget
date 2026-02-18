# Standards References

satlinkbudget implements models from international telecommunications and space standards. This document describes each standard, how it is implemented, and what simplifications are made.

---

## ITU-R Recommendations

### ITU-R P.676-13 — Gaseous Attenuation

**Title:** Attenuation by atmospheric gases and related effects

**Scope:** Models oxygen and water-vapor absorption from 1 GHz to 1000 GHz along slant paths through the atmosphere.

**Implementation:**
- `atmosphere._gaseous.specific_attenuation_oxygen(freq_ghz, pressure_hpa, temp_k)`
- `atmosphere._gaseous.specific_attenuation_water_vapor(freq_ghz, pressure_hpa, temp_k, rho_g_m3)`
- `atmosphere._gaseous.gaseous_attenuation_slant(freq_ghz, elevation_deg, ...)`

**Approach:** Simplified Annex 2 model using equivalent absorption heights for O₂ and H₂O. Slant-path integration via `A = (γ_o · h_o + γ_w · h_w) / sin(El)`.

**Simplifications:**
- Uses the simplified wideband model (Annex 2), not the full line-by-line summation of Annex 1
- Standard atmosphere profiles; does not accept arbitrary pressure/temperature profiles
- Valid for frequencies up to ~350 GHz (full P.676 extends to 1000 GHz)

**Key validation:** 60 GHz O₂ resonance peak produces ~15 dB/km specific attenuation; 22.235 GHz H₂O line visible in frequency sweep.

---

### ITU-R P.618-14 — Rain Attenuation (Earth-Space Paths)

**Title:** Propagation data and prediction methods required for the design of Earth-space telecommunication systems

**Scope:** Prediction of rain attenuation exceeded for a given percentage of time on slant paths.

**Implementation:**
- `atmosphere._rain.rain_attenuation_exceeded(freq_ghz, elevation_deg, rain_rate_001_mm_h, ...)`
- Uses specific attenuation coefficients from P.838

**Approach:** Implements the complete step-by-step procedure of P.618 Section 2.2.1.1:
1. Rain height from P.839
2. Slant path length through rain
3. Horizontal reduction factor
4. Vertical adjustment factor
5. Effective path length

**Simplifications:**
- Uses the P.839 mean rain height rather than monthly statistics
- Percentage-time scaling uses the simplified power-law approximation

---

### ITU-R P.838-3 — Specific Rain Attenuation

**Title:** Specific attenuation model for rain for use in prediction methods

**Scope:** Regression coefficients k and α for computing rain specific attenuation γ_R = k · R^α [dB/km].

**Implementation:**
- `atmosphere._rain.rain_specific_attenuation_coefficients(freq_ghz, elevation_deg, polarization_tilt_deg)`
- `atmosphere._rain.rain_specific_attenuation(freq_ghz, rain_rate_mm_h, ...)`

**Approach:** Implements the full frequency-dependent regression from Table 1 (k_H, k_V, α_H, α_V) with polarization-tilt interpolation.

**Key validation:** 12 GHz, 50 mm/h → ~5.6 dB/km specific attenuation.

---

### ITU-R P.839-4 — Rain Height

**Title:** Rain height model for prediction methods

**Scope:** Mean annual rain height as a function of latitude.

**Implementation:**
- `atmosphere._rain.effective_rain_height_km(latitude_deg)`

**Approach:** Simplified latitude-dependent model from Recommendation text.

---

### ITU-R P.840-8 — Cloud and Fog Attenuation

**Title:** Attenuation due to clouds and fog

**Scope:** Rayleigh-regime attenuation from liquid water droplets.

**Implementation:**
- `atmosphere._cloud.cloud_specific_attenuation_coefficient(freq_ghz, cloud_temp_k)`
- `atmosphere._cloud.cloud_attenuation(freq_ghz, elevation_deg, lwc_kg_m2, cloud_temp_k)`

**Approach:** K_l coefficient from the double-Debye relaxation model, applied as `A = K_l · LWC / sin(El)`.

**Simplifications:** Cloud temperature assumed uniform (single value, default 273.15 K).

---

### ITU-R P.531-14 — Ionospheric Effects

**Title:** Ionospheric propagation data and prediction methods required for the design of satellite services and systems

**Scope:** Scintillation, Faraday rotation, group delay, and related ionospheric effects.

**Implementation:**
- `atmosphere._scintillation.scintillation_index_s4(freq_ghz, ...)`
- `atmosphere._scintillation.ionospheric_scintillation_loss(freq_ghz, elevation_deg, ...)`

**Approach:** S₄ scintillation index model with frequency scaling (∝ f^−1.5), geomagnetic latitude dependence, and diurnal variation.

**Simplifications:**
- Uses simplified S₄ model rather than full probabilistic characterization
- Faraday rotation and group delay not modeled
- Most significant below ~4 GHz; negligible at S-band and above

---

## ECSS Standards

### ECSS-E-ST-50C — Communications

**Relevance:** European standard for space-to-ground and inter-satellite communication system design. Defines link budget methodology, margin policy, and test requirements.

**Implementation notes:** satlinkbudget's link budget line items follow the ECSS-E-ST-50C convention for gain/loss accounting. The sign convention (FSPL and atmospheric losses as positive numbers subtracted in the budget) matches standard practice.

### ECSS-E-ST-10-04C — Space Environment

**Relevance:** Defines the space environment models including ionospheric electron content, solar flux indices, and radiation belt models.

**Implementation notes:** Solar flux index (F10.7) and geomagnetic latitude are used as inputs to the P.531 scintillation model.

---

## CCSDS Standards

### CCSDS 401.0-B — RF and Modulation

**Title:** Radio Frequency and Modulation Systems — Part 1: Earth Stations and Spacecraft

**Relevance:** Defines standard frequency bands, modulation formats, and spectral masks for space communications.

**Implementation notes:** The modulation schemes (BPSK, QPSK, 8PSK) and their theoretical BER curves match CCSDS 401.0-B definitions. Frequency band definitions in the component database align with CCSDS allocations.

### CCSDS 131.0-B — TM Synchronization and Channel Coding

**Title:** TM Synchronization and Channel Coding

**Relevance:** Defines turbo, LDPC, and convolutional coding schemes for space telemetry.

**Implementation notes:** Coding gains used in `modem._coding` are representative values from CCSDS 131.0-B performance curves at BER = 10⁻⁵:
- Convolutional R=1/2, K=7: ~5.0 dB coding gain
- Turbo R=1/2: ~8.0 dB coding gain
- LDPC R=1/2: ~7.5 dB coding gain

---

## Reference Textbooks

### Space Mission Analysis and Design (SMAD)

**Authors:** Wertz, Everett, Puschell (eds.)
**Edition:** 4th edition (Microcosm Press, 2011)
**Relevant chapter:** Chapter 13 — Communications Architecture

satlinkbudget's link budget methodology closely follows SMAD Chapter 13. The UHF CubeSat downlink example validates within 0.5 dB of the SMAD reference calculation.

### Satellite Communications (Roddy)

**Author:** Dennis Roddy
**Edition:** 4th edition (McGraw-Hill, 2006)

Reference for system noise temperature cascading (Friis formula), G/T figure of merit, and rain attenuation models.

### Satellite Communications Systems (Maral & Bousquet)

**Authors:** Gérard Maral, Michel Bousquet
**Edition:** 5th edition (Wiley, 2009)

Reference for atmospheric propagation models, orbit geometry, and link availability calculations.

---

## Implementation Notes

### Where We Simplify

| Area | Full Standard | satlinkbudget | Impact |
|------|--------------|---------------|--------|
| P.676 gaseous | Line-by-line summation (Annex 1) | Wideband model (Annex 2) | < 0.1 dB below 100 GHz |
| P.618 rain | Monthly rain statistics | Annual mean rain rate | ±1 dB for typical locations |
| P.840 cloud | Height-dependent LWC profile | Single slab model | < 0.3 dB at most frequencies |
| Orbit propagation | Full numerical perturbations | Keplerian + J2 secular | Position error < 10 km/day |
| Antenna patterns | Full 3D pattern | Peak gain + pointing loss | Valid within main beam |

These simplifications are appropriate for preliminary mission design and trade studies. For detailed mission design and operational planning, use the full ITU-R procedures (e.g., via the `itur` Python package) or mission-specific tools.
