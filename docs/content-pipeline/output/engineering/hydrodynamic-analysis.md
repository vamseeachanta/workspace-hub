---
title: "Hydrodynamic Analysis"
description: "Boundary Element Method (BEM) based potential flow analysis for computing RAOs, added mass, radiation damping, and wave excitation forces on offshore..."
keywords: "hydrodynamics, bem, rao, added-mass, damping, wave-loads, wamit, aqwa, orcawave"
author: "ACE Engineer"
url: "/knowledge/engineering/hydrodynamic-analysis"
canonical: "https://aceengineer.com/knowledge/engineering/hydrodynamic-analysis"
domain: "engineering"
---

# Hydrodynamic Analysis

*By [ACE Engineer](https://aceengineer.com) -- Expert Offshore and Marine Engineering Consulting*

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

- **Related entity**: AQWA Solver
- **Related entity**: OrcaWave Solver
- **Related entity**: Diffraction Analysis System
- **Related concept**: Wave Theory for Offshore Engineering
- **Related concept**: Seakeeping and 6-DOF Ship Dynamics
- **Related standard**: DNV-RP-C205

---

## Work With Us

ACE Engineer provides expert engineering consulting across offshore, marine, and subsea disciplines. Our team combines deep domain expertise with modern computational tools to deliver reliable, auditable results.

[Contact us](https://aceengineer.com/contact) to discuss how we can support your project.

*Visit [aceengineer.com](https://aceengineer.com) for our full range of services.*

