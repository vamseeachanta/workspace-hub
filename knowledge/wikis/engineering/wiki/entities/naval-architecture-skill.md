---
title: "Naval Architecture Skill"
tags: [naval-architecture, hydrostatics, stability, seakeeping, rao, roll-damping, diffraction]
sources:
  - skills-metadata
added: 2026-04-09
last_updated: 2026-04-09
---

# Naval Architecture Skill

Comprehensive marine vessel analysis skill covering hydrostatics, stability, seakeeping, RAO interpretation, and diffraction analysis review. Encodes the physics causal chain that must be verified in order for any diffraction analysis.

## Physics Causal Chain

The fundamental verification ordering:

1. **Geometry** -> 2. **Hydrostatics** -> 3. **Stability** -> 4. **Natural Periods** -> 5. **Hydrodynamic Coefficients** -> 6. **Wave Excitation** -> 7. **Motion Response** -> 8. **Damping Assessment**

Each step depends on the ones before it. Skip a step, get wrong answers.

## Key Formulas

**Metacentric height**: `GM_T = C(4,4) / (rho * g * V)` where rho=1025 kg/m^3

**Natural period**: `T_n,i = 2*pi * sqrt((M_ii + A_ii(omega_n)) / C_ii)` — iterative, requires sweeping added mass across frequency grid.

**Critical damping ratio**: `zeta(omega) = B_44(omega) / (2 * sqrt((M_44 + A_44(omega)) * C_44))`

## Hull-Type Characteristics

| Hull Type | Roll T_n | Key Feature |
|-----------|---------|-------------|
| Barge | 6-15s | Sharp heave resonance, low damping, negligible coupling |
| FPSO/Tanker | 12-20s | Surge-pitch coupling, viscous roll damping dominates |
| Semi-sub | 30-60s | Column interference, higher radiation damping |
| Spar | 25-35s (heave) | Deep draft reduces short-period excitation |
| LNGC | Similar to FPSO | Roll damping critical for cargo transfer |

## Roll Damping Components (DNV-RP-C205 S7)

Total = radiation + skin friction + eddy-making + bilge keel + lift damping. If radiation-only critical damping ratio is less than 2% at resonance, viscous damping modelling is essential. Typical radiation-only ranges: Barge 0.5-2%, Ship/FPSO 1-5%, Semi-sub 2-8%.

## Class Society Submission Requirements

A diffraction analysis submission must include: hull geometry and mesh quality assessment, hydrostatic verification, natural period estimates cross-referenced to RAO peaks, added mass and damping coefficient plots, wave excitation forces, displacement RAOs with phase, roll damping assessment with viscous justification, convergence study, and model test comparison if available.

## Cross-References

- **Related entity**: [OrcaFlex Solver](../entities/orcaflex-solver.md)
- **Related entity**: [AQWA Solver](../entities/aqwa-solver.md)
- **Related entity**: [Diffraction Analysis System](../entities/diffraction-analysis-system.md)
- **Related concept**: [CFD Offshore Hydrodynamics](../concepts/cfd-offshore-hydrodynamics.md)
- **Related standard**: [DNV-RP-C205](../standards/dnv-rp-c205.md)
