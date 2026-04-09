---
title: "CFD for Offshore Applications"
tags: [cfd, openfoam, fluent, scour, wave-loading, hydrodynamics, offshore]
sources:
  - career-learnings
added: 2026-04-09
last_updated: 2026-04-09
---

# CFD for Offshore Applications

Computational fluid dynamics (CFD) applied to offshore structures for wave loading, scour
assessment, and hydrodynamic analysis. Common tools include OpenFOAM and ANSYS Fluent.

## Wave Loading

- **Morison equation**: Valid for small D/lambda ratio (< 0.2); drag + inertia force on slender members
- **Diffraction analysis**: Required for larger structures where D/lambda > 0.2
- KC number determines drag vs inertia dominance: KC > 20 is drag-dominated

## Morison Coefficients (DNVGL-RP-C205)

| Coefficient | Value | Application |
|-------------|-------|-------------|
| Cd (drag) | 1.05 | Cylindrical members |
| Cm (inertia) | 2.0 | Cylindrical members |

## Scour Assessment

- **Horseshoe vortex** mechanism around monopile foundations drives local scour
- Shields parameter determines onset of sediment transport
- Scour depth estimate: 1.3 pile diameters for steady current (Sumer & Fredsoe)

## Turbulence Modelling

- k-omega SST reliable for separated flows around bluff bodies
- Domain sizing minimum: upstream 10D, downstream 20D, lateral 5D

## Design Patterns

- Morison equation valid for D/lambda < 0.2; diffraction important for larger structures
- KC number determines drag vs inertia dominance: KC > 20 drag-dominated
- Scour depth estimate: 1.3 pile diameters for steady current

## Cross-References

- **Related entity**: [[fea-structural-analysis]] (CFD loads as FEA input)
- **Related entity**: [[pipeline-integrity]] (scour-induced free spans affect pipeline integrity)
- **Cross-wiki (engineering)**: [CFD Offshore Hydrodynamics](../../../engineering/wiki/concepts/cfd-offshore-hydrodynamics.md) — comprehensive CFD methodology: domain sizing, turbulence models, mesh requirements, and validation approach
