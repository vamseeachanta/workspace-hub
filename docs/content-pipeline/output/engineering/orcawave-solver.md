---
title: "OrcaWave Solver"
description: "OrcaWave is Orcina's hydrodynamic diffraction/radiation solver, designed for tight integration with OrcaFlex. It computes added mass, radiation damping,..."
keywords: "orcawave, diffraction, radiation, qtf, hydrodynamics, orcina"
author: "ACE Engineer"
url: "/knowledge/engineering/orcawave-solver"
canonical: "https://aceengineer.com/knowledge/engineering/orcawave-solver"
domain: "engineering"
---

# OrcaWave Solver

*By [ACE Engineer](https://aceengineer.com) -- Expert Offshore and Marine Engineering Consulting*

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

A canonical single-command pipeline exists (implemented in ):
`.owr` -> RAO extraction -> coordinate transform -> OrcaFlex vessel type YAML

This automates what was previously a manual multi-step process involving separate bridge pieces (orcaflex_exporter.py, bemrosetta converters, convert_to_orcaflex.py).

## Unit Conventions

- Frequencies reported in **Hz descending** — must convert to rad/s and reverse sort for comparison with AQWA
- Phase convention: **Orcina lag** — differs from AQWA ISO lead convention
- Rotational RAOs in **radians/m** — convert with `np.degrees` for deg/m output

## Cross-References

- **Related entity**: OrcaFlex Solver
- **Related entity**: AQWA Solver
- **Related entity**: BEMRosetta Tool
- **Related entity**: Diffraction Analysis System
- **Related workflow**: Solver Debugging Protocol

---

## Work With Us

ACE Engineer provides expert engineering consulting across offshore, marine, and subsea disciplines. Our team combines deep domain expertise with modern computational tools to deliver reliable, auditable results.

[Contact us](https://aceengineer.com/contact) to discuss how we can support your project.

*Visit [aceengineer.com](https://aceengineer.com) for our full range of services.*

