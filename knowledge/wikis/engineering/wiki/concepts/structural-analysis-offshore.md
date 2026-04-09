---
title: "Structural Analysis for Offshore Structures"
tags: [structural, mechanics, dnv, buckling, uls, als, beam-theory, stress-analysis, tubular-joints]
sources:
  - skills-metadata
added: 2026-04-09
last_updated: 2026-04-09
---

# Structural Analysis for Offshore Structures

Expert structural analysis per DNV/API/ISO codes covering ULS/ALS limit state checks, buckling, combined loading, tubular joint capacity, and stiffened panel design. The digitalmodel skill (v1.1.0) encodes all standard formulas and design check workflows.

## Core Knowledge Areas

### Section Properties
Circular tube: `A = pi/4*(D^2-d^2)`, `I = pi/64*(D^4-d^4)`, `r = sqrt(I/A)`.

### Column Buckling (DNV-OS-C101 / DNV-RP-C201)
- Euler critical load: `P_cr = pi^2*E*I/(K*L)^2`
- Reduced slenderness: `lambda_bar = (K*L/r)*sqrt(fy/E)/pi`
- European column curve 'a' (alpha=0.21 for welded tubes)
- Design resistance: `N_b_Rd = chi*A*fy/gamma_M`

### Tubular Joint Design (DNV-RP-C203)
Geometric parameters: `beta=d/D`, `gamma=D/(2T)`, `tau=t/T`.
Validity: `0.2 <= beta <= 1.0`, `10 <= gamma <= 50`, `theta >= 30 deg`.
T/Y joint axial capacity: `N_cap = Qu*fy*T^2/sin(theta)`.

### ULS Combined Loading
- Linear: `N/N_Rd + My/My_Rd + Mz/Mz_Rd <= 1.0`
- Eurocode: `(N/N_Rd)^2 + (My/My_Rd + Mz/Mz_Rd) <= 1.0`
- Use conservative max of both.

### ALS Dented Pipe (DNV-RP-F110)
- `d/D < 6%` acceptable; `6-20%` engineering assessment; `>20%` repair.

### Stiffened Panel Buckling
Plate critical stress: `sigma_cr = k*pi^2*E/(12*(1-nu^2))*(t/b)^2` with k=4.0 for long plates.

## Applicable Codes

**DNV:** OS-C101, RP-C201 (buckling), RP-C203 (fatigue/joints), RP-C205 (environmental), ST-0126 (wind turbine supports), OS-E301 (mooring).

**API:** RP 2A (fixed platforms), RP 2FPS (floating), RP 2SK (mooring).

**Other:** ISO 19902 (fixed steel offshore), Eurocode 3 (EN 1993), AISC 360.

## Cross-References

- **Related concept**: [FEA Structural Analysis](../concepts/fea-structural-analysis.md)
- **Related concept**: [S-N Curve Fatigue Definitions](../concepts/sn-curve-fatigue-definitions.md)
- **Related concept**: [Pipeline Integrity Assessment](../concepts/pipeline-integrity-assessment.md)
- **Related standard**: [DNV-RP-C203](../standards/dnv-rp-c203.md)
- **Related standard**: [API 579-1/ASME FFS-1](../standards/api-579-ffs.md)
