---
name: crossprovider codex openfoam-on-gpu-claw-remains-cpu-mpi-bound-gpu-o
description: OpenFOAM on gpu-claw remains CPU/MPI-bound; GPU offload not justified
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cfd-profiling, gpu-optimization, workload-characterization]
---

gpu-claw has 2× RTX 3090 but OpenFOAM workload (VOF/MULES/PIMPLE) is CPU/MPI-bound at 8 ranks without GPU acceleration bridge (no PETSc/AmgX/petsc4Foam). Prior benchmark: 0.5899 s/step @ 8 ranks CPU, 1.64× faster than comparison node. GPU tuning (clock locking, power limits, persistence) premature until solver integration exists.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
