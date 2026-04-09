---
title: "FEA Structural Analysis"
description: "Finite Element Analysis (FEA) for structural engineering in offshore and subsea applications. Covers meshing strategy, boundary conditions, convergence..."
keywords: "fea, finite-element, meshing, boundary-conditions, convergence, fatigue"
author: "ACE Engineer"
url: "/knowledge/engineering/fea-structural-analysis"
canonical: "https://aceengineer.com/knowledge/engineering/fea-structural-analysis"
domain: "engineering"
---

# FEA Structural Analysis

*By [ACE Engineer](https://aceengineer.com) -- Expert Offshore and Marine Engineering Consulting*

Finite Element Analysis (FEA) for structural engineering in offshore and subsea applications. Covers meshing strategy, boundary conditions, convergence checks, and fatigue post-processing — the areas where errors are most common and most consequential.

## Meshing Strategy

### Element Size

Element size is driven by the **stress gradient** at the location of interest, not by the overall model size.

| Location | Minimum Requirement | Rationale |
|----------|-------------------|-----------|
| Through-thickness bending | 3 elements minimum through wall thickness | Captures bending stress distribution |
| Stress concentration (notch, hole) | Element size < 0.25 x notch radius | Resolves the gradient around the feature |
| Weld toe (fatigue hot-spot) | 0.4t x 0.4t at the toe, per IIW or DNV | Required for hot-spot stress extrapolation |
| Far-field (away from interest) | Coarse — 5-10x the fine mesh size | Reduces computation without affecting accuracy |

### Element Type Selection

| Criterion | Shell Elements | Solid Elements |
|-----------|---------------|----------------|
| t/L ratio | Valid when t/L < 0.1 | Required when t/L > 0.1 |
| Through-thickness detail | Not captured (assumes linear distribution) | Full 3D stress state |
| Computation cost | Low | High (3-10x more DOFs) |
| Typical use | Plate/shell structures, hulls, jackets | Local details: lugs, padeyes, joints, weld roots |

**Transition**: when mixing shell and solid regions, use constraint equations or shell-to-solid coupling elements to avoid artificial stress discontinuities at the interface.

### Mesh Convergence

Refine the mesh at the location of interest until the **stress change is less than 5%** between successive refinements. This is a non-negotiable check. Report the convergence study results — reviewers and class societies expect it.

## Boundary Conditions

### Common Errors

Boundary conditions are the most frequent source of FEA errors:

| BC Type | Problem | Better Alternative |
|---------|---------|-------------------|
| Fully fixed (encastre) | Overstiffens the support — attracts unrealistic stress | Spring supports calibrated to actual stiffness |
| Symmetry plane | Missing rotational DOF constraint | Check all 6 DOFs at symmetry plane |
| Point load | Creates artificial stress singularity | Distribute load over a pad or contact area |
| Rigid connection (MPC) | Locks relative rotation — unrealistic for bolted joints | Use connector elements or contact with friction |

### Verification: Reaction Force Check

After solving, **confirm that the sum of reaction forces equals the applied loads**. This is the most basic and most important sanity check. If the reactions do not balance, the model has a rigid-body mode, an unconstrained DOF, or a load application error.

## Contact and Connections

| Physical Joint | FEA Representation |
|---------------|-------------------|
| Welded joint | Mesh tie (node-to-surface constraint) |
| Bolted joint | Pretensioned connector + contact with friction |
| Bearing surface | Contact (surface-to-surface) with appropriate friction |
| Sliding support | Frictionless contact or roller BC |

For **fatigue-critical welded joints**, the weld geometry should be explicitly modeled (weld profile, root gap) when assessing weld root cracking. For weld toe cracking, the hot-spot stress method allows assessment without modeling the weld geometry explicitly.

## Nonlinear Analysis

Enable **NLGEOM** (geometric nonlinearity) when:

- Deflection exceeds 0.1 times the span length
- Buckling or post-buckling behavior is expected
- Large rotation occurs (e.g., lifting analysis, cable structures)
- Contact is present (contact is inherently nonlinear)

Material nonlinearity (plasticity) is required for:

- Collapse analysis per codes (API 2A, NORSOK N-004)
- Strain-based design (reeling installation, lateral buckling)
- Level 3 fitness-for-service assessments (API 579)

## Fatigue Post-Processing

### Hot-Spot Stress Method

Per **IIW** or **DNV-RP-C203**, hot-spot stress is extrapolated from stresses at defined distances from the weld toe to the toe location. This removes the mesh-size sensitivity of the peak stress at the singularity.

For shell models:
- Read stress at 0.5t and 1.5t from the weld toe
- Linear extrapolation to the toe

For solid models:
- Read stress at 0.4t and 1.0t from the weld toe
- Linear extrapolation to the toe

### Stress Singularities

Point loads, sharp re-entrant corners, and crack tips produce **mathematically infinite stress** as the mesh is refined. Do not report peak stress at these locations as a design stress. Instead:

- **Linearise** the stress through the thickness (membrane + bending) and ignore the peak component
- Use the **hot-spot stress** extrapolation method for fatigue
- For fracture mechanics, use J-integral or stress intensity factor (K) from a dedicated crack model

## Key Patterns

1. **Check reaction forces = applied loads** — first thing after every solve
2. **Singularities at point loads: use linearisation not peak** — the peak value is mesh-dependent and physically meaningless
3. **Shell valid when t/L < 0.1, solid for local detail** — mixing requires careful coupling
4. **NLGEOM when deflection > 0.1 x span** — linear analysis becomes non-conservative for flexible structures

## Cross-References

- **Related concept**: viv-riser-fatigue — fatigue S-N curves and hot-spot stress for riser girth welds
- **Related concept**: pipeline-integrity-assessment — FEA-based Level 3 fitness-for-service
- **Related concept**: cfd-offshore-hydrodynamics — CFD loads as input to structural FEA
- **Cross-wiki (naval-architecture)**: Ship Structural Design — FEA for hull girder strength, plate buckling, and fatigue of ship structures
- **Source**: Career Learnings Seed

---

## Work With Us

ACE Engineer provides expert engineering consulting across offshore, marine, and subsea disciplines. Our team combines deep domain expertise with modern computational tools to deliver reliable, auditable results.

[Contact us](https://aceengineer.com/contact) to discuss how we can support your project.

*Visit [aceengineer.com](https://aceengineer.com) for our full range of services.*

