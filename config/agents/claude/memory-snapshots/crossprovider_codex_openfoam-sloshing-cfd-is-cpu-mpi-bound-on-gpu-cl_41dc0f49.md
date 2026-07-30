---
name: crossprovider codex openfoam-sloshing-cfd-is-cpu-mpi-bound-on-gpu-cl
description: OpenFOAM sloshing CFD is CPU/MPI-bound on gpu-claw; GPU offload not viable
metadata:
  type: reference
  source: codex
  bridged: 2026-07-15
  tags: [cfd, gpu-claw, openfoam, performance]
---

VOF/MULES/PIMPLE algorithms dominate compute; no PETSc/AmgX/petsc4Foam bridge available. Current lane: 8-rank CPU/MPI, GPU idle (P8 state, 420W default). GPU acceleration not worthwhile; CPU remains correct path.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
