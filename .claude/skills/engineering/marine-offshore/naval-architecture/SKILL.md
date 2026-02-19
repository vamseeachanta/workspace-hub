---
name: naval-architecture
version: "1.0.0"
category: engineering
description: "Marine/offshore vessel analysis — hydrostatics, stability, seakeeping, RAOs"
capabilities: []
requires: []
see_also: []
---
# Naval Architecture

## Activation

Use this skill when working on marine/offshore vessel analysis: hydrostatics, stability, seakeeping, RAO interpretation, natural period estimation, roll damping assessment, classification submissions, or report generation for diffraction analysis.

## Physics Causal Chain

The fundamental ordering for any diffraction analysis review:

1. **Geometry** -> 2. **Hydrostatics** -> 3. **Stability** -> 4. **Natural Periods** -> 5. **Hydrodynamic Coefficients** -> 6. **Wave Excitation** -> 7. **Motion Response** -> 8. **Damping Assessment**

Each step depends on the ones before it. Always verify in this order.

## Section 1: Hydrostatics & Initial Stability

Key formulas:

- `GM_T = C(4,4) / (rho * g * V)` where rho=1025 kg/m^3, g=9.81 m/s^2
- `GM_L = C(5,5) / (rho * g * V)`
- `BM_T = I_xx / V` (waterplane second moment / displaced volume)
- `BM_L = I_yy / V`
- `KB = z_B` (vertical CoB coordinate)
- Cross-check: `GM_T ~ KB + BM_T - KG`

Status thresholds:

- `GM_T > 1.0m` -> OK (green) per DNV-OS-C301
- `0 < GM_T < 1.0m` -> WARNING
- `GM_T <= 0` -> UNSTABLE (red)

Radii of gyration: `r_xx = sqrt(I_44/M)`, `r_yy = sqrt(I_55/M)`, `r_zz = sqrt(I_66/M)`

## Section 2: Seakeeping Fundamentals

Natural period computation:

- `T_n,i = 2*pi * sqrt((M_ii + A_ii(omega_n)) / C_ii)`
- Iterative: sweep `A_ii(omega)` across frequency grid, find intersection
- For surge/sway/yaw: natural period depends on mooring stiffness (not in diffraction)

RAO interpretation:

- RAO = Response Amplitude Operator = motion per unit wave amplitude
- Translational DOFs: m/m (dimensionless), Rotational DOFs: deg/m
- Peak RAO should occur near natural period
- Phase = 0 deg: in-phase with wave, -90 deg: lagging, +90 deg: leading
- ~180 deg phase jump near resonance = quasi-static to resonant transition
- Phase meaningless at near-zero amplitude

## Section 3: Hydrodynamic Coefficients

Added mass A(omega):

- Represents entrained water inertia
- Generally increases at low frequencies
- Infinite frequency value A(inf) needed for retardation functions (time-domain)

Radiation damping B(omega):

- Energy lost to radiated waves
- Peaks near natural frequency
- Zero at omega=0 and omega->inf

Coupling assessment:

- Significant coupling: `|A_ij(omega)| / max(|A_ii(omega)|, |A_jj(omega)|) > 5%`
- Surge-Pitch (A_15/A_51): ship-like forms, CoG offset
- Sway-Roll (A_24/A_42): asymmetric or ship-like forms
- Sway-Yaw (A_26/A_62): beam-sea effect
- Symmetric bodies: cross-couplings ~ 0

## Section 4: Roll Damping Components (DNV-RP-C205 S7)

Total roll damping = radiation + viscous components:

- Radiation damping: from potential flow (BEM solvers)
- Skin friction: proportional to wetted surface
- Eddy-making: from bilge keels, bilge radius
- Bilge keel: dominant viscous component
- Lift damping: forward-speed dependent

Critical damping ratio: `zeta(omega) = B_44(omega) / (2 * sqrt((M_44 + A_44(omega)) * C_44))`

Typical radiation-only ranges:

- Barge: 0.5-2% critical
- Ship/FPSO: 1-5% critical
- Semi-sub: 2-8% critical

If `zeta < 2%` at resonance: viscous damping essential.

## Section 5: Motion Criteria

DNV comfort criteria (ISO 6954):

- Vertical acceleration < 0.2g (habitable spaces)
- Lateral acceleration < 0.1g

Operational limits vary by activity:

- Crane operations: typically Hs < 2.5m
- Cargo transfer: typically Hs < 2.0m
- Personnel transfer: typically Hs < 1.5m

## Section 6: Hull-Type Characteristics

### Barge

- Sharp heave resonance (low damping, high Awp)
- Roll T_n typically 6-15s
- Negligible coupling for symmetric box
- Wide beam -> large GM_T (resonance peaks are the concern)

### FPSO/Tanker

- Surge-pitch coupling (A_15) significant
- Roll T_n 12-20s
- Low radiation roll damping -- viscous dominates (bilge keels critical)
- Yaw at quartering seas important for mooring

### Semi-sub

- Heave T_n 18-25s (small Awp)
- Roll/pitch T_n 30-60s
- Column interference patterns in load RAOs
- Higher radiation damping than monohulls

### Spar

- Heave T_n 25-35s (very small Awp)
- Deep draft reduces short-period excitation
- VIM not captured by potential flow

### LNGC

- Similar to FPSO
- Prismatic midship
- Internal sloshing not captured
- Roll damping critical for cargo transfer

### Cylinder/Sphere

- Validation cases
- Analytical solutions: McCamy-Fuchs (cylinder), Hulme (sphere)

## Section 7: Class Society Submission Requirements

What reviewers expect in a diffraction analysis submission:

1. Hull geometry description and mesh quality assessment
2. Hydrostatic verification (volume, CoB, GM cross-check)
3. Natural period estimates with cross-reference to RAO peaks
4. Added mass and damping coefficient plots (diagonal terms minimum)
5. Wave excitation forces (load RAOs)
6. Displacement RAOs with phase
7. Roll damping assessment and justification for viscous additions
8. Convergence study (mesh density sensitivity)
9. Comparison with model test data (if available)

## Section 8: Common Pitfalls

- **OrcaWave frequencies in Hz descending** -- multiply by 2*pi, sort ascending
- **Rotational RAOs in rad/m** -- convert to deg/m for reporting
- **AQWA phase convention (ISO lead)** vs **OrcaWave (Orcina lag)** -- normalize before comparison
- **Mesh quality**: panels must be roughly square, area ratio < 10
- **QTF settings**: must NOT be set when QTF is disabled in OrcaWave
- **AQWA QPPL DIFF** required for diffraction (not just QPPL)
- **Zero std dev** in correlation: handle NaN gracefully (e.g. yaw at head seas)

## Section 9: Reference Bibliography

1. Newman (1977) -- Marine Hydrodynamics. MIT Press.
2. Faltinsen (1990) -- Sea Loads on Ships and Offshore Structures. Cambridge.
3. Journee & Massie (2001) -- Offshore Hydromechanics. TU Delft.
4. Lee (1995) -- WAMIT Theory Manual. MIT.
5. Chakrabarti (2005) -- Handbook of Offshore Engineering. Elsevier.
6. Chakrabarti (1987) -- Hydrodynamics of Offshore Structures.
7. DNV-RP-C205 (2021) -- Environmental Conditions and Environmental Loads.
8. DNV-OS-C301 -- Stability and Watertight Integrity.
9. DNV-OS-E301 -- Position Mooring.
10. ABS -- Guide for Building and Classing Floating Offshore Installations.

## Notation

- DOFs: 1=Surge, 2=Sway, 3=Heave, 4=Roll, 5=Pitch, 6=Yaw
- Coordinate system: x-forward, z-up, right-hand rule
- SI units: kg, m, s (unless otherwise noted)
