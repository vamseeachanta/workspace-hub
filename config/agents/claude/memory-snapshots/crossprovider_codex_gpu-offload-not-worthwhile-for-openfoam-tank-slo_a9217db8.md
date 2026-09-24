---
name: crossprovider codex gpu-offload-not-worthwhile-for-openfoam-tank-slo
description: GPU offload not worthwhile for OpenFOAM tank sloshing
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cfd, gpu-compute, performance, openfoam]
---

CPU/MPI at 8 ranks remains the correct lane. No PETSc/AmgX/petsc4Foam bridge exists, and VOF/MULES/PIMPLE solvers are CPU-bound. Historical benchmark: 0.5899 s/step @ 8 ranks on 216k-cell interFoam.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
