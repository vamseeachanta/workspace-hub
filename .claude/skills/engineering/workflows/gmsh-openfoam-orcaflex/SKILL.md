---
name: gmsh-openfoam-orcaflex
description: "Multi-physics simulation pipeline \u2014 Gmsh mesh generation \u2192\
  \ OpenFOAM CFD \u2192 OrcaFlex structural/mooring analysis.  Agent-callable end-to-end\
  \ workflow that passes geometry, fluid loads, and structural response through three\
  \ solvers in sequence with validated handoffs at each step.  Stub/mock fallbacks\
  \ for environments without solver licenses.\n"
version: 1.0.0
updated: 2026-02-24
category: engineering
triggers:
- multi-physics pipeline
- Gmsh OpenFOAM OrcaFlex
- CFD to structural pipeline
- fluid loads to OrcaFlex
- hydrodynamic structural chain
- H1 multi-physics workflow
- cylinder in flow pipeline
- gmsh openfoam orcaflex
capabilities:
- input_generation
- execution
- output_parsing
- failure_diagnosis
- validation
- stub_mode
requires:
- gmsh-meshing
- openfoam
- orcaflex-modeling
- cfd-pipeline
see_also:
- gmsh-openfoam-orcaflex-quick-invocation
- gmsh-openfoam-orcaflex-pipeline-architecture
- gmsh-openfoam-orcaflex-file-map
- gmsh-openfoam-orcaflex-output-format-pipelineresultsjson
- gmsh-openfoam-orcaflex-gate-1-mesh-quality
- gmsh-openfoam-orcaflex-converter-1-gmsh-msh-openfoam-polymesh
- gmsh-openfoam-orcaflex-stub-mode-details
- gmsh-openfoam-orcaflex-real-mode-requirements
- gmsh-openfoam-orcaflex-agent-usage-pattern
- gmsh-openfoam-orcaflex-error-propagation-map
wrk_ref: WRK-380
spec_ref: specs/modules/wrk-380-gmsh-openfoam-orcaflex-pipeline.md
tags: []
---

# Gmsh Openfoam Orcaflex

## Related Skills

- [cfd-pipeline](../cfd-pipeline/SKILL.md) — Gmsh→OpenFOAM→ParaView workflow
- [hydrodynamic-pipeline](../hydrodynamic-pipeline/SKILL.md) — OrcaWave→OrcaFlex
- [gmsh-meshing](../../cad/gmsh-meshing/SKILL.md) — Gmsh mesh generation
- [openfoam](../../cfd/openfoam/SKILL.md) — OpenFOAM solver interface
- [orcaflex-modeling](../../marine-offshore/orcaflex-modeling/SKILL.md) — OrcaFlex API

---

## Version History

- **1.0.0** (2026-02-24): Initial multi-physics pipeline skill (WRK-380).
  40/40 tests passing in stub mode. All acceptance criteria met.

## Sub-Skills

- [Quick Invocation](quick-invocation/SKILL.md)
- [Pipeline Architecture](pipeline-architecture/SKILL.md)
- [File Map](file-map/SKILL.md)
- [Output Format: pipeline_results.json](output-format-pipelineresultsjson/SKILL.md)
- [Gate 1 — Mesh Quality (+1)](gate-1-mesh-quality/SKILL.md)
- [Converter 1: Gmsh .msh → OpenFOAM polyMesh (+1)](converter-1-gmsh-msh-openfoam-polymesh/SKILL.md)
- [Stub Mode Details](stub-mode-details/SKILL.md)
- [Real Mode Requirements](real-mode-requirements/SKILL.md)
- [Agent Usage Pattern](agent-usage-pattern/SKILL.md)
- [Error Propagation Map](error-propagation-map/SKILL.md)
