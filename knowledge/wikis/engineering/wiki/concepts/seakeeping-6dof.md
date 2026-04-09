---
title: "Seakeeping and 6-DOF Ship Dynamics"
tags: [6dof, seakeeping, ship-dynamics, vessel-motions, natural-frequency, equations-of-motion]
sources:
  - skills-metadata
  - closed-issues
added: 2026-04-09
last_updated: 2026-04-09
---

# Seakeeping and 6-DOF Ship Dynamics

6-DOF (six degrees of freedom) ship dynamics — surge, sway, heave, roll, pitch, yaw — is the foundation of all vessel motion prediction. The digitalmodel `seakeeping` module (implemented in #1984) provides RAO-based motion response, spectral analysis, operability assessment, and extreme motion prediction.

## Core Analysis Types

- **Equations of motion**: Set up and solve 6DOF coupled equations with mass, added mass, damping, stiffness, and excitation
- **Natural frequencies**: Calculate natural periods for all DOFs — iterative for frequency-dependent added mass
- **Frequency-domain analysis**: RAO-based motion prediction from wave spectra
- **Time-domain simulation**: Integrate equations of motion with retardation functions
- **Operability**: Predict operational windows from motion limits and sea state scatter diagrams
- **Extreme motions**: Most probable maximum response for a given exposure duration

## SeakeepingAnalysis API

```python
class SeakeepingAnalysis:
    def motion_response(self, sea_state: SeaState) -> MotionResponse
    def motion_spectra(self, sea_state: SeaState) -> dict
    def operability(self, limit_table: dict) -> OperabilityResult
    def extreme_motion(self, exposure_hours: float) -> MotionExtreme
```

Accepts RAO data from Capytaine, AQWA, or OrcaWave. Integrates with existing hydrodynamics module for wave spectra and signal-analysis module for statistics.

## Motion Criteria

| Activity | Typical Limit |
|----------|--------------|
| Crane operations | Hs < 2.5m |
| Cargo transfer | Hs < 2.0m |
| Personnel transfer | Hs < 1.5m |
| DNV comfort (vertical accel) | < 0.2g |
| DNV comfort (lateral accel) | < 0.1g |

## Cross-References

- **Related entity**: [Naval Architecture Skill](../entities/naval-architecture-skill.md)
- **Related entity**: [OrcaFlex Solver](../entities/orcaflex-solver.md)
- **Related concept**: [Wave Theory for Offshore Engineering](../concepts/wave-theory-offshore.md)
- **Related standard**: [DNV-RP-C205](../standards/dnv-rp-c205.md)
- **Cross-wiki (naval-architecture)**: [Seakeeping and Ship Motions](../../../naval-architecture/wiki/concepts/seakeeping.md) — 6-DOF motion theory (RAOs, operability criteria) implemented in the digitalmodel seakeeping module
- **Cross-wiki (naval-architecture)**: [Ship Hydrostatics](../../../naval-architecture/wiki/concepts/hydrostatics.md) — hydrostatic stiffness (displacement, waterplane area, metacentric height) as inputs to 6-DOF equations of motion
- **Cross-wiki (naval-architecture)**: [Ship Stability](../../../naval-architecture/wiki/concepts/stability.md) — stability (GM, GZ curves) as fundamental constraint on vessel motion response
- **Cross-wiki (marine-engineering)**: [Long-Period Swell & Resonance](../../../marine-engineering/wiki/concepts/long-period-swell-resonance.md) — resonant 6-DOF motion amplification from long-period swell at LNG terminals
