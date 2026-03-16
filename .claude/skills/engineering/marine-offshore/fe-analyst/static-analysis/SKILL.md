---
name: fe-analyst-static-analysis
description: 'Sub-skill of fe-analyst: Static Analysis (+3).'
version: 1.0.0
category: engineering
type: reference
scripts_exempt: true
---

# Static Analysis (+3)

## Static Analysis

- Purpose: Establish equilibrium position under static loads (gravity, current, pretension)
- OrcaFlex: `CalculateStatics()`
- Outputs: Static position, static tensions, static bending moments
- Convergence criteria: max residual force < 1e-3 kN


## Dynamic Analysis

- Purpose: Time-domain simulation under wave + current
- OrcaFlex: `RunSimulation()`, stage duration, ramp time
- Minimum ramp: 1× Tp to settle hydrodynamic transients
- Minimum simulation duration: 3 hours (10,800 s) for statistical convergence
- Output extraction: Every 0.1–0.2 s (Nyquist for 5×Tp minimum)


## Modal Analysis

- Purpose: Natural frequencies and mode shapes (VIV susceptibility)
- Key output: Fundamental period T1 [s] vs. wave/vortex shedding period
- Strouhal criterion: `f_vs = St × U / D` where St ≈ 0.2 (subcritical)
- Flag if `|T1 - T_wave| / T_wave < 0.10` (resonance proximity)


## Fatigue Analysis

- Purpose: Accumulated damage over service life
- Method: Time-domain rainflow counting OR frequency-domain spectral
- S-N curve: DNV-OS-F101 D-curve for girth welds
- SCF: DNVGL-RP-C203 hot spot or notch stress
- Target: D < 1.0 (design life ≥ 20 yr with factor of 10)

---
