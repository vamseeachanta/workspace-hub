---
title: "FEA Structural Analysis"
tags: [fea, finite-element, structural, meshing, fatigue, offshore]
sources:
  - career-learnings
added: 2026-04-09
last_updated: 2026-04-09
---

# FEA Structural Analysis

Finite element analysis (FEA) for offshore and structural engineering applications. Covers
meshing strategy, boundary condition modelling, convergence checks, and fatigue post-processing.

## Meshing Best Practices

- Element size driven by stress gradient — minimum 3 elements through thickness for bending-dominated problems
- Convergence check: mesh refine until stress change < 5% between refinement levels
- Shell vs solid elements: shell valid when t/L < 0.1; solid for local detail models
- Contact elements for bearing problems; mesh tie for welded joints

## Boundary Conditions

- Must match physical constraints — fixed BC overstiffens the response
- Spring supports better represent real structural flexibility
- Always check reaction forces sum to applied loads (equilibrium check)

## Nonlinearity

- Geometric nonlinearity (NLGEOM) required when deflection > 0.1 x span
- Material nonlinearity for plastic hinge or ultimate strength assessments

## Stress Post-Processing

| Issue | Guidance |
|-------|----------|
| Singularities at point loads | Use stress linearisation, not peak stress |
| Hot-spot stress for fatigue | Extrapolation per IIW or DNVGL-RP-C203 |
| Convergence | Refine mesh until stress change < 5% |

## Design Patterns

- Always check reaction forces sum to applied loads (equilibrium check)
- Singularities at point loads: use stress linearisation, not peak stress
- Geometric nonlinearity (NLGEOM) required when deflection > 0.1 x span

## Cross-References

- **Related entity**: [[orcaflex-viv-analysis]] (fatigue assessment downstream of VIV)
- **Related entity**: [[pipeline-integrity]] (FFS assessment may use FEA Level 3)
- **Related entity**: [[cfd-offshore]] (CFD loads as FEA input)
- **Cross-wiki (engineering)**: [FEA Structural Analysis](../../../engineering/wiki/concepts/fea-structural-analysis.md) — detailed FEA methodology: meshing strategy, boundary conditions, convergence checks, hot-spot stress extrapolation
- **Cross-wiki (engineering)**: [Structural Analysis for Offshore Structures](../../../engineering/wiki/concepts/structural-analysis-offshore.md) -- similar slugs (75%); similar titles (58%); shared tags: structural; shared keywords: analysis, cross-references, design, related, structural
- **Cross-wiki (naval-architecture)**: [Ship Structural Design](../../../naval-architecture/wiki/concepts/ship-structures.md) -- similar slugs (53%); similar titles (62%); shared tags: fatigue
