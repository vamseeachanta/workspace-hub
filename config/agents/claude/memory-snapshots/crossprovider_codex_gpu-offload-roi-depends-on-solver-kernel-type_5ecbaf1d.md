---
name: crossprovider codex gpu-offload-roi-depends-on-solver-kernel-type
description: GPU offload ROI depends on solver kernel type
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [performance, gpu-computing, solver-architecture]
---

GPU acceleration is not cost-effective when solver kernels (VOF/MULES/PIMPLE) dominate over math libraries and no GPU-accelerated library bridge exists (e.g., no PETSc/AmgX/petsc4Foam). CPU/MPI at saturated rank count remains the correct lane.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
