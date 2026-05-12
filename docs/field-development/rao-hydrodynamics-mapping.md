# RAO & Motion Analysis Coverage Mapping

**Source:** LinkedIn post "P10: Motion Analysis and RAOs" by Mehdi Mosafer  
**Extraction Date:** 2026-05-12  
**Post URL:** https://www.linkedin.com/feed/update/urn:li:activity:7459845568270348288/

## 1. Source Content Summary

### What is a Response Amplitude Operator (RAO)?

An RAO describes how a structure (vessel or subsea asset) responds to waves at different frequencies.

**Definition:**
```
RAO = Response / Wave amplitude
```

For each degree of freedom (DOF), we can compute:
- Motion RAOs (heave, roll, pitch, sway, surge, yaw)
- Load RAOs (force or moment per unit wave amplitude)

**Common Examples:**
- Heave RAO (vertical motion response)
- Roll Motion RAO (lateral rotation response)
- Pitch Load RAO (longitudinal bending moment response)

### Why RAOs Are Important

RAOs are the backbone of:
- **Vessel motion analysis** — predict ship motions in waves
- **Operability assessments** — determine safe operating windows (sea state limits)
- **DP analysis** — dynamic positioning thrust allocation and vessel positioning
- **Offshore lifting studies** — crane load estimation, motion compensation
- **Pipelay analyses** — pipe-lay vessel motion and tension management

### RAOs Enable Prediction Of:
- Motions (displacement, velocity)
- Accelerations (affecting cargo and equipment)
- Dynamic loads (forces and moments on structures)

### Resonance: The Critical Part

The most important region is **near the structure's natural period**. When wave frequency aligns with natural frequency, motions can increase dramatically (resonance amplification).

This requires accurate natural period estimation:
- Natural heave period — function of displacement and waterplane area
- Natural pitch period — function of length and longitudinal metacentric height
- Natural roll period — function of beam and transverse metacentric height

---

## 2. Component Inventory & Standards References

| Component | Standard/Reference | Description |
|-----------|-------------------|-------------|
| RAO computation | DNV-RP-H103, USNA EN400 | Frequency-domain hydrodynamic response |
| Natural periods | PNA Vol III, Journée & Massie | Ship geometry-based period estimation |
| Wave spectrum integration | DNV-RP-H103 | Spectral motion prediction |
| Encounter frequency | Ship theory | Relative wave-vessel frequency |
| Motion criteria | DNV-RP-A203, USNA | Operability thresholds (motion sickness, cargo/equipment limits) |
| 6-DOF motion | IACS, API RP 2A | Coupled surge, sway, heave, roll, pitch, yaw |
| Frequency response | Controls theory, Marine dynamics | Linear system response analysis |

---

## 3. Operational Workflows

### Workflow A: Static RAO-Based Operability Assessment
```
1. Load vessel RAO table (from OrcaWave or empirical database)
2. Define sea state (spectrum type: Pierson-Moskowitz, JONSWAP)
3. For each wave heading / speed combination:
   a. Interpolate RAOs at encounter frequency
   b. Integrate wave spectrum × RAO² → response spectrum
   c. Extract statistical parameters (Hs_motion, T_peak_motion, max expected)
   d. Compare against operability criteria
   e. Determine "go/no-go" decision
```

### Workflow B: Natural Period Estimation (Design Phase)
```
1. Vessel geometry (displacement, GM, waterplane area, L, B)
   → natural_heave_period()
   → natural_pitch_period()
   → natural_roll_period()
2. Check resonance risk zones (period ±20%)
3. If critical resonance zone in expected operating spectrum:
   a. Design ballast trim to shift natural periods
   b. Add bilge keels / anti-roll fins
   c. Re-estimate and re-validate
```

### Workflow C: Dynamic Lifting / Pipelay
```
1. Crane RAO (heave motion transfer function from vessel to load)
2. Sea state spectrum + vessel motion spectrum
   → dynamic tension estimation
3. Auto-compensation control (if active system)
```

---

## 4. Code Coverage Map

### STRONG Coverage ✓

| Component | Module | Status | Tests |
|-----------|--------|--------|-------|
| RAO data I/O (CSV, YAML) | `orcawave/rao_processing.py` | ✓ STRONG | Yes |
| Amplitude ↔ phase ↔ complex conversion | `orcawave/rao_processing.py` | ✓ STRONG | Yes |
| Natural period estimation (heave, pitch, roll) | `naval_architecture/seakeeping.py` | ✓ STRONG | Yes |
| Encounter frequency | `naval_architecture/seakeeping.py` | ✓ STRONG | Yes |
| Motion statistics (RMS, peak from spectrum) | `orcawave/motion_statistics.py` | ✓ STRONG | Yes |
| Hydrodynamic coefficients (drag, added mass) | `orcawave/hydro_coefficients.py` | ✓ STRONG | Yes |

### PARTIAL Coverage ◐

| Component | Module | Gap | Priority |
|-----------|--------|-----|----------|
| Spectral integration (RAO × spectrum) | `orcawave/motion_statistics.py` | Limited heading/speed coverage in examples | Medium |
| Operability criteria database | N/A — skill only | No standardized rule set for different vessel types | Medium |
| 6-DOF coupled motion | `orcawave/motion_statistics.py` | Single-DOF focus; multi-body not integrated | Low |
| Dynamic pipelay analysis | OrcaFlex skill | Explicit module doesn't exist in codebase | Low |

### NO Coverage (GAP) ✗

| Component | Why Missing | Suggested Scope |
|-----------|------------|-----------------|
| RAO generation from first principles (diffraction) | Requires OrcaWave external tool | Provide wrapper for OrcaWave batch export + parsing |
| Resonance safety margin checker | Domain-specific risk assessment | Small utility: `resonance_risk(natural_period, spectrum_peak)` |
| Operability decision tree | Human-in-loop; no universal rule | Rules engine with vessel-class/cargo-type branching |

---

## 5. Quick Reference Tables

### Natural Period Formulas (Frequency-Domain)

| Parameter | Formula | Source | Units |
|-----------|---------|--------|-------|
| T_heave | 2π√(m / ρgA_wp) | PNA III | seconds |
| T_pitch | 2π(k_yy / √(g·GML)) where k_yy ≈ 0.25L | PNA III | seconds |
| T_roll | 2π(k_xx / √(g·GM)) where k_xx ≈ 0.40B | PNA III | seconds |
| ω_encounter | ω_wave − (ω_wave² / g)·V·cos(χ) | Ship theory | rad/s |

### Standards & References

- **DNV-RP-H103**: Modelling and Analysis of Marine Operations
- **PNA Vol III**: Motions in Waves and Controllability
- **USNA EN400**: Ship Hydrodynamics (Chapter 8: Seakeeping)
- **Journée & Massie**: Offshore Hydromechanics (free textbook)
- **DNV-RP-A203**: Offshore and Subsea Pipeline Systems

---

## 6. Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│           Wave Environment (Spectrum)                │
│     [Pierson-Moskowitz, JONSWAP, Bretschneider]     │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │   RAO Table          │
          │  (Amplitude & Phase) │
          │  [orcawave/rao_*]    │
          └────────┬─────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
        ▼                     ▼
   ┌─────────────┐      ┌──────────────────┐
   │  Natural    │      │ Spectral Int.    │
   │  Periods    │      │ (Response Stats) │
   │[seakeeping] │      │[motion_stats]    │
   └─────────────┘      └────────┬─────────┘
        │                        │
        │                        ▼
        │               ┌──────────────────┐
        │               │ Response Spectrum│
        │               │ (Hs, Tp, PDF)    │
        │               └────────┬─────────┘
        │                        │
        └────────────┬───────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │  Operability Check   │
          │  (Motion Criteria)   │
          │ [YES / NO / CAUTION] │
          └──────────────────────┘
```

---

## 7. Integration Points with digitalmodel

### Existing Integrations
- `orcawave/vessel_database.py` — RAO lookup by vessel class
- `orcaflex/installation_analysis.py` — uses motion_statistics for sling load estimation
- `naval_architecture/seakeeping.py` — natural period input to resonance checks

### Recommended Next Steps
1. **Enhance motion_statistics** — add spectral moment calculations (m0, m1, m2)
2. **Add operability rules** — branching logic for different vessel types and cargoes
3. **Resonance warning system** — automatic flag when operating near critical periods
4. **Pipelay module** — integrated crane/pipe dynamics (currently OrcaFlex-only)

---

## 8. Related Concepts to Document in llm-wiki

1. **Hydrodynamic damping** — frequency-dependent energy dissipation
2. **Added mass** — effective mass increase due to fluid inertia
3. **Wave drift forces** — slow-drift second-order effects
4. **Roll stabilization** — bilge keels, fin stabilizers, active systems
5. **Frequency response function (FRF)** — concept behind RAO
6. **Operability windows** — sea state / heading combinations safe for operations
7. **Motion sickness incidence (MSI)** — human factors threshold

---

## Extraction Notes

- **Author Expertise**: Mehdi Mosafer — Subsea/Pipeline/Installation/Project Field Engineer with focus on hydrodynamic analysis and marine operations
- **Target Audience**: Engineers with background in "Mechanical Vibrations" and "Automatic Control" — assumes systems theory knowledge
- **Key Insight**: RAOs are a practical form of frequency response functions (FRF) widely used in offshore engineering, not just academic theory
- **Tone**: Educational, practical focus on real-world operability assessment

---

**Status:** Ready for llm-wiki ingestion  
**Format:** Structured knowledge article with code mapping  
**Audience:** Field engineers, simulation analysts, DP operators
