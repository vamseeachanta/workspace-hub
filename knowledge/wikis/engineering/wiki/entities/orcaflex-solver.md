---
title: "OrcaFlex Solver"
tags: [orcaflex, orcfxapi, solver, riser, mooring, marine-dynamics]
sources:
  - career-learnings-seed
  - dark-intelligence-extractions
added: 2026-04-08
last_updated: 2026-04-08
---

# OrcaFlex Solver

OrcaFlex is a commercial marine dynamics solver by Orcina, widely used for nonlinear time-domain and frequency-domain analysis of risers, moorings, and marine structures. It is the primary licensed solver in the workspace-hub ecosystem, accessed via OrcFxAPI Python bindings.

## OrcFxAPI Python Bindings

OrcFxAPI provides full programmatic control over OrcaFlex models — create, modify, run, and post-process simulations without the GUI. Key automation patterns:

- Load models: `model = OrcFxAPI.Model(filename)`
- Modify objects, run statics/dynamics, extract results
- Batch automation via the [Solver Queue](../entities/solver-queue.md)

## Frequency-Domain Conventions

These conventions are critical when comparing OrcaFlex output to other solvers (e.g., AQWA):

| Property | Convention | Notes |
|----------|-----------|-------|
| `.frequencies` | Returns **Hz** (not rad/s) | Convert to rad/s: `ω = 2π × f` |
| Frequency order | **Descending** | Highest frequency first — reverse before comparing to AQWA |
| `displacementRAOs` shape | `(nheading, nfreq, 6)` | Complex-valued array; 6 DOF per frequency per heading |
| Rotational RAOs | **radians/m** | Convert with `np.degrees()` for deg/m output |

## Common Use Cases

- **VIV analysis**: Vortex-induced vibration fatigue assessment for risers and pipelines
- **Riser fatigue**: Combined wave + VIV fatigue life estimation using S-N curves
- **Mooring analysis**: Quasi-static and dynamic mooring system design and verification
- **Installation simulation**: Vessel motion, crane operations, pipelay, and lowering through splash zone

## Unit Traps

When correlating OrcaFlex results with other hydrodynamic solvers:

1. **Frequency units**: OrcaFlex/OrcaWave uses Hz descending; AQWA uses rad/s. Mismatched units produce negative correlations.
2. **Rotational RAO units**: rad/m vs deg/m — a factor-of-57.3 error if not converted.
3. **Array shape**: Always verify `(nheading, nfreq, 6)` vs `(nfreq, nheading, 6)` — transposed arrays silently produce wrong results.

## Cross-References

- **Related concept**: [VIV Riser Fatigue](../concepts/viv-riser-fatigue.md)
- **Related concept**: [S-N Curve Fatigue Definitions](../concepts/sn-curve-fatigue-definitions.md)
- **Related entity**: [AQWA Solver](../entities/aqwa-solver.md)
- **Related entity**: [Solver Queue](../entities/solver-queue.md)
- **Related workflow**: [Solver Debugging Protocol](../workflows/solver-debugging-protocol.md)
- **Cross-wiki (marine-engineering)**: [LNG Carrier Mooring](../../../marine-engineering/wiki/entities/lng-carrier-mooring.md) — OrcaFlex used for mooring analysis of LNG carriers at terminals
- **Cross-wiki (marine-engineering)**: [Mooring Line Failure](../../../marine-engineering/wiki/concepts/mooring-line-failure.md) — OrcaFlex models dynamic mooring loads that drive line failure assessment
