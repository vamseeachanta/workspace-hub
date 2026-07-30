---
name: crossprovider codex openfoam-sloshing-workload-is-cpu-mpi-bound-not-
description: OpenFOAM sloshing workload is CPU/MPI-bound, not GPU-accelerable
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [gpu-claw, openfoam, architecture-decision, cfd]
---

VOF/MULES/PIMPLE solver stack dominates runtime; GPU RTX 3090 offload not worthwhile without expensive PETSc/AmgX/petsc4Foam bridges. Current validated lane: 8-rank MPI on CPU at 0.5899 s/step on 216k-cell meshes. GPU clock tuning will not improve this workload.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
