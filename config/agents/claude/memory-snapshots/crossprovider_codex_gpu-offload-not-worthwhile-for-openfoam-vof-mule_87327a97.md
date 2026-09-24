---
name: crossprovider codex gpu-offload-not-worthwhile-for-openfoam-vof-mule
description: GPU offload not worthwhile for OpenFOAM VOF/MULES/PIMPLE
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cfd, openfoam, performance, gpu]
---

On interFoam sloshing workloads, CPU/MPI at 8 ranks is the correct lane. GPU offload (PETSc/AmgX/petsc4Foam) is not currently available and would not repay the overhead; the bottleneck is VOF advection and pressure coupling, not linear algebra. RTX 3090 @ idle P8 with default 420 W limits.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
