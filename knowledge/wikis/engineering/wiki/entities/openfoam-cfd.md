---
title: "OpenFOAM CFD"
tags: [openfoam, cfd, simulation, meshing, turbulence, multiphase, linux]
sources:
  - skills-metadata
added: 2026-04-09
last_updated: 2026-04-09
---

# OpenFOAM CFD

OpenFOAM is an open-source CFD toolkit used in the workspace-hub ecosystem for offshore hydrodynamic simulations. The skill covers case setup, CLI execution, output parsing, failure diagnosis, and validation. It runs on Linux only and depends on the `gmsh-meshing` skill for mesh generation.

## Capabilities

- **Case setup**: Generate system dictionaries (controlDict, fvSchemes, fvSolution)
- **Solver execution**: Serial and parallel (simpleFoam, pimpleFoam, interFoam)
- **Log parsing**: Residual extraction, convergence monitoring, Courant number tracking
- **Failure diagnosis**: FPE, divergence, mesh quality issues, BC mismatches
- **Validation**: Benchmark against cavity, pitzDaily, damBreak reference cases
- **Post-processing**: foamToVTK conversion for ParaView visualization

## Analysis Workflow Stages

The OpenFOAM analysis skill defines 6 stages:
1. Problem definition
2. Case setup (geometry, BCs, material properties)
3. Meshing (blockMesh or gmsh import)
4. Execution (serial/parallel solver run)
5. Post-processing (field extraction, visualization)
6. Reporting (parametric report generation)

## Key Integration Points

- **Gmsh meshing**: Upstream mesh generation with quality control
- **ParaView**: Downstream visualization via VTK export
- **digitalmodel**: CFD results feed into wave loading and VIV assessments

## Cross-References

- **Related concept**: [CFD Offshore Hydrodynamics](../concepts/cfd-offshore-hydrodynamics.md)
- **Related concept**: [FEA Structural Analysis](../concepts/fea-structural-analysis.md)
- **Related entity**: [digitalmodel](../entities/digitalmodel.md)
