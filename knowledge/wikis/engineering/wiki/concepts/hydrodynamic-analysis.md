---
title: "Hydrodynamic Analysis"
tags: [hydrodynamics, bem, rao, added-mass, damping, wave-loads, wamit, aqwa, orcawave]
sources:
  - skills-metadata
added: 2026-04-09
last_updated: 2026-04-09
---

# Hydrodynamic Analysis

Boundary Element Method (BEM) based potential flow analysis for computing RAOs, added mass, radiation damping, and wave excitation forces on offshore structures. Three solver implementations exist in the ecosystem: WAMIT, AQWA, and OrcaWave.

## Core Outputs

| Output | Description |
|--------|-------------|
| RAOs | Response Amplitude Operators — motion per unit wave amplitude. Translational: m/m, Rotational: deg/m |
| Added mass A(omega) | Frequency-dependent entrained water inertia. Generally increases at low frequencies |
| Radiation damping B(omega) | Energy lost to radiated waves. Peaks near natural frequency, zero at omega=0 and omega->inf |
| Wave excitation | Froude-Krylov + diffraction forces on restrained body |
| QTFs | Quadratic Transfer Functions — second-order drift forces for low-frequency motion |

## Analysis Workflow

1. **Geometry discretization**: Create panel mesh of wetted hull surface
2. **Solve radiation problem**: Unit-amplitude forced oscillation in each DOF
3. **Solve diffraction problem**: Incident wave scattered by restrained body
4. **Extract coefficients**: Added mass, damping, wave excitation at each frequency
5. **Compute RAOs**: Solve equations of motion for motion response per unit wave amplitude
6. **Validate**: Check convergence (mesh density), cross-reference natural periods with RAO peaks

## Coupling Assessment

Significant coupling exists when `|A_ij(omega)| / max(|A_ii(omega)|, |A_jj(omega)|) > 5%`. Common couplings: Surge-Pitch (A_15) for ship-like forms, Sway-Roll (A_24) for asymmetric forms, Sway-Yaw (A_26) in beam seas.

## Cross-References

- **Related entity**: [AQWA Solver](../entities/aqwa-solver.md)
- **Related entity**: [OrcaWave Solver](../entities/orcawave-solver.md)
- **Related entity**: [Diffraction Analysis System](../entities/diffraction-analysis-system.md)
- **Related concept**: [Wave Theory for Offshore Engineering](../concepts/wave-theory-offshore.md)
- **Related concept**: [Seakeeping and 6-DOF Ship Dynamics](../concepts/seakeeping-6dof.md)
- **Related standard**: [DNV-RP-C205](../standards/dnv-rp-c205.md)
