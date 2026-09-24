---
name: crossprovider codex gpu-offload-viability-depends-on-kernel-profile-
description: GPU offload viability depends on kernel profile, not hardware spec
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [gpu-offload, performance, profiling]
---

GPU availability (RTX 3090, 420W default) does not predict offload ROI. Workloads dominated by I/O-bound kernels (VOF/MULES/PIMPLE flux correction without PETSc bridge) remain CPU/MPI-bound. Profile before assuming GPU acceleration; CPU/8-rank may be correct lane despite GPU presence.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
