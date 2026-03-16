---
name: openfoam
version: 1.0.0
category: engineering
description: "OpenFOAM AI Interface Skill \u2014 case setup, CLI execution, output\
  \ parsing, failure diagnosis, validation"
tags:
- openfoam
- cfd
- simulation
- meshing
- solver
- turbulence
- multiphase
- incompressible
- parallel
platforms:
- linux
invocation: openfoam
depends_on:
- gmsh-meshing
capabilities:
- input-generation
- execution
- output-parsing
- failure-diagnosis
- validation
requires: []
see_also:
- openfoam-installation
- openfoam-11-case-directory-structure
- openfoam-15-fvsolution
- openfoam-19-blockmeshdict
- openfoam-21-environment-setup
- openfoam-31-solver-log-residual-format
- openfoam-41-error-message-format
- openfoam-51-y-verification
- openfoam-61-upstream-gmsh-to-openfoam
scripts_exempt: true
---

# Openfoam

## When to Use This Skill

Use this skill when you need to:
- Set up an OpenFOAM CFD case from scratch (geometry, mesh, BCs, solver)
- Generate valid system dictionaries (controlDict, fvSchemes, fvSolution)
- Run solvers in serial or parallel (simpleFoam, pimpleFoam, interFoam)
- Parse solver logs for residuals, convergence, and Courant numbers
- Diagnose solver failures (FPE, divergence, mesh quality, BC mismatches)
- Validate results against known benchmarks (cavity, pitzDaily, damBreak)
- Convert results for visualization (foamToVTK for ParaView)

## Sub-Skills

- [Installation](installation/SKILL.md)
- [1.1 Case Directory Structure (+3)](11-case-directory-structure/SKILL.md)
- [1.5 fvSolution (+3)](15-fvsolution/SKILL.md)
- [1.9 blockMeshDict (+1)](19-blockmeshdict/SKILL.md)
- [2.1 Environment Setup (+6)](21-environment-setup/SKILL.md)
- [3.1 Solver Log Residual Format (+5)](31-solver-log-residual-format/SKILL.md)
- [4.1 Error Message Format (+2)](41-error-message-format/SKILL.md)
- [5.1 y+ Verification (+5)](51-y-verification/SKILL.md)
- [6.1 Upstream: Gmsh to OpenFOAM (+3)](61-upstream-gmsh-to-openfoam/SKILL.md)
