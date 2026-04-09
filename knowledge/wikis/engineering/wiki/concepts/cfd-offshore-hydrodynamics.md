---
title: "CFD for Offshore Hydrodynamics"
tags: [cfd, openfoam, wave-loading, morison, scour, viv]
sources:
  - career-learnings-seed
added: 2026-04-08
last_updated: 2026-04-08
---

# CFD for Offshore Hydrodynamics

Computational Fluid Dynamics applied to offshore structures — wave loading, current forces, scour, and vortex-induced vibration. Practical guidance on when CFD is necessary versus simpler methods, and how to set up reliable offshore CFD models.

## When CFD vs. Simplified Methods

The first decision in any hydrodynamic analysis is whether CFD is needed at all.

### Morison Equation Regime

The **Morison equation** (drag + inertia force per unit length on a cylinder) is valid when the structure is small relative to the wave:

**D/lambda < 0.2** (where D = diameter, lambda = wavelength)

| D/lambda | Regime | Method |
|----------|--------|--------|
| < 0.2 | Drag/inertia dominated | Morison equation |
| 0.2 - 0.5 | Transition | Morison with diffraction correction, or panel method |
| > 0.5 | Diffraction dominated | Panel method (WAMIT, AQWA) or CFD |

For most jacket members, conductor pipes, and risers, D/lambda < 0.2 and Morison is appropriate. For gravity-based structures, spar platforms, large-diameter monopiles, and floating hulls, diffraction analysis is required.

### Keulegan-Carpenter Number

The **KC number** (KC = U_max * T / D) determines the flow regime around cylinders in oscillatory flow:

| KC Range | Regime | Cd/Cm Behavior |
|----------|--------|----------------|
| KC < 3 | Inertia dominated | Cm dominant, Cd negligible |
| 3 < KC < 20 | Transition | Both Cd and Cm significant |
| KC > 20 | Drag dominated | Cd dominant, Cm reduces |

When KC > 20, the flow behaves quasi-steadily and drag forces dominate — relevant for slender members in strong currents.

## Standard Hydrodynamic Coefficients

Per **DNV-RP-C205** for smooth and rough cylinders:

| Surface | Cd | Cm | Notes |
|---------|-----|-----|-------|
| Smooth cylinder | 1.05 | 2.0 | Clean, no marine growth |
| Rough cylinder (k/D > 0.01) | 1.05 increased by roughness | 1.8 | Marine growth zone |
| Cylinder with strakes | 1.6-2.0 | — | VIV suppression, increased drag penalty |

These values assume subcritical Reynolds numbers. At supercritical Re (large diameters, high velocities), Cd drops — but DNV-RP-C205 recommends not reducing Cd below the subcritical value for design.

## CFD Setup — OpenFOAM and ANSYS Fluent

### Domain Sizing

Proper domain sizing prevents artificial blockage and allows the wake to develop:

| Boundary | Distance from Structure | Rationale |
|----------|------------------------|-----------|
| Upstream (inlet) | 10D | Wave/current development length |
| Downstream (outlet) | 20D | Wake dissipation — avoids outlet BC reflection |
| Lateral (sides) | 5D per side | Prevents blockage ratio > 5% |
| Top (atmosphere) | Above free surface + wave height | Free surface must not interact with boundary |
| Bottom (seabed) | Physical seabed or 5D if no seabed interaction | Seabed boundary layer for scour studies |

### Turbulence Model

**k-omega SST** is the standard choice for offshore hydrodynamics:

- Handles wall-bounded flows and separated flows well
- Blends k-omega (near wall) with k-epsilon (free stream)
- Required for any application with flow separation: VIV, scour, wave breaking

For free-surface flows, use **Volume of Fluid (VOF)** method with interFoam (OpenFOAM) or equivalent multiphase solver.

### Mesh Requirements

- **y+ < 1** for wall-resolved boundary layer (required for accurate drag prediction)
- **Inflation layers**: 15-20 layers with growth ratio 1.1-1.2
- **Free surface refinement**: at least 20 cells per wave height, 100 cells per wavelength
- **Wake region**: refined zone extending 10-15D downstream

## Scour

Scour around monopiles and jacket legs is driven by the **horseshoe vortex** system at the upstream face and lee-wake vortices downstream.

### Onset: Shields Parameter

Scour initiates when the bed shear stress exceeds the critical Shields parameter (theta_cr) for the sediment:

- Fine sand (d50 = 0.2 mm): theta_cr ~ 0.05
- Medium sand (d50 = 0.5 mm): theta_cr ~ 0.04
- Coarse sand (d50 = 2 mm): theta_cr ~ 0.03

### Equilibrium Scour Depth

Per **Sumer and Fredsoe**:

| Flow Condition | Equilibrium Scour Depth (S/D) |
|----------------|------------------------------|
| Steady current | 1.3D |
| Waves only | 0.5-1.0D (depends on KC) |
| Combined waves + current | 1.0-1.3D |

Scour protection design (rock dump, mattresses, frond mats) must account for the expected scour development rate and the time to install protection after pile driving.

## Key Patterns

1. **Cd = 1.05, Cm = 2.0 for cylinders (DNV-RP-C205)** — default starting point for smooth cylinders
2. **KC > 20 = drag-dominated** — simplifies the force calculation to quasi-steady drag
3. **Scour depth ~ 1.3D for steady current (Sumer and Fredsoe)** — use this for initial sizing of scour protection
4. **k-omega SST for separated flows** — do not use k-epsilon for VIV, scour, or wake studies

## Practical Guidance

- **Validate against experiments first**: before trusting a CFD model for design, validate Cd and vortex shedding frequency (Strouhal number ~ 0.2) against published experimental data for the same Re range.
- **2D vs. 3D**: 2D CFD overpredicts drag and VIV amplitude because it cannot capture 3D correlation length effects. Use 2D for screening only; 3D for design.
- **Wave generation**: use relaxation zones (not just inlet boundary conditions) to prevent wave reflection. In OpenFOAM, the waves2Foam or olaFlow toolboxes provide this.
- **Transient simulations**: offshore CFD is inherently transient. Steady-state RANS is not appropriate for vortex shedding, wave loading, or scour development. Use URANS or LES with time steps satisfying CFL < 1.

## Cross-References

- **Related concept**: [[viv-riser-fatigue]] — VIV loads computed by CFD as input to fatigue analysis
- **Related concept**: [[fea-structural-analysis]] — CFD pressure fields mapped to FEA structural models
- **Related concept**: [[pipeline-integrity-assessment]] — hydrodynamic loads on free-spanning pipelines
- **Cross-wiki (marine-engineering)**: [Long-Period Swell & Resonance](../../../marine-engineering/wiki/concepts/long-period-swell-resonance.md) — CFD and diffraction methods for modelling resonant vessel response to long-period waves
- **Cross-wiki (marine-engineering)**: [Mooring Line Failure](../../../marine-engineering/wiki/concepts/mooring-line-failure.md) — hydrodynamic loads on moored vessels driving mooring line forces
- **Cross-wiki (naval-architecture)**: [Seakeeping and Ship Motions](../../../naval-architecture/wiki/concepts/seakeeping.md) — CFD for vessel RAO computation and seakeeping optimization
- **Cross-wiki (naval-architecture)**: [Ship Resistance and Propulsion](../../../naval-architecture/wiki/concepts/resistance-propulsion.md) — CFD for resistance prediction and propeller-hull interaction
- **Source**: [Career Learnings Seed](../sources/career-learnings-seed.md)
