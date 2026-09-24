---
name: crossprovider codex openfoam-cpu-mpi-preferred-over-gpu-for-vof-work
description: OpenFOAM CPU/MPI preferred over GPU for VOF workloads
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cfd, performance, optimization, openfoam]
---

VOF/MULES/PIMPLE-dominated OpenFOAM simulations run more efficiently on CPU/MPI (8 ranks) than GPU. GPU offload is worthwhile only with a PETSc/AmgX/petsc4Foam bridge, which does not exist in this setup; the workload is compute-bound on CPU.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
