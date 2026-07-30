---
name: crossprovider codex gpu-offload-roi-in-cfd-cpu-mpi-is-correct-lane-w
description: GPU offload ROI in CFD: CPU/MPI is correct lane without PETSc/AmgX bridge
metadata:
  type: reference
  source: codex
  bridged: 2026-07-15
  tags: [hpc, cfd, performance, gpu-compute]
---

OpenFOAM workloads using VOF/MULES/PIMPLE are CPU/MPI-bound. GPU acceleration without a PETSc-CUDA or AmgX bridge does not justify the complexity cost. Validate baseline CPU/MPI scaling (e.g., 8 ranks) before proposing GPU lanes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
