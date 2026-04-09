---
title: "OrcaWave Solver"
tags: [orcawave, diffraction, radiation, qtf, hydrodynamics, orcina]
sources:
  - skills-metadata
added: 2026-04-09
last_updated: 2026-04-09
---

# OrcaWave Solver

OrcaWave is Orcina's hydrodynamic diffraction/radiation solver, designed for tight integration with OrcaFlex. It computes added mass, radiation damping, wave excitation forces, and RAOs using panel methods (BEM).

## Sub-Skills

| Sub-Skill | Purpose |
|-----------|---------|
| analysis | Core diffraction/radiation analysis workflows |
| qtf-analysis | Quadratic Transfer Function (second-order) analysis |
| damping-sweep | Damping coefficient parametric studies |
| mesh-generation | Panel mesh creation and refinement |
| multi-body | Multi-body hydrodynamic interaction |
| to-orcaflex | Export results to OrcaFlex vessel type format |
| aqwa-benchmark | Cross-validation against AQWA results |

## OrcaWave-to-OrcaFlex Pipeline

A canonical single-command pipeline exists (implemented in #1768):
`.owr` -> RAO extraction -> coordinate transform -> OrcaFlex vessel type YAML

This automates what was previously a manual multi-step process involving separate bridge pieces (orcaflex_exporter.py, bemrosetta converters, convert_to_orcaflex.py).

## Unit Conventions

- Frequencies reported in **Hz descending** — must convert to rad/s and reverse sort for comparison with AQWA
- Phase convention: **Orcina lag** — differs from AQWA ISO lead convention
- Rotational RAOs in **radians/m** — convert with `np.degrees()` for deg/m output

## Cross-References

- **Related entity**: [OrcaFlex Solver](../entities/orcaflex-solver.md)
- **Related entity**: [AQWA Solver](../entities/aqwa-solver.md)
- **Related entity**: [BEMRosetta Tool](../entities/bemrosetta-tool.md)
- **Related entity**: [Diffraction Analysis System](../entities/diffraction-analysis-system.md)
- **Related workflow**: [Solver Debugging Protocol](../workflows/solver-debugging-protocol.md)
