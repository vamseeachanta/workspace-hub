---
name: crossprovider codex gpu-offload-requires-workload-specific-justifica
description: GPU offload requires workload-specific justification
metadata:
  type: reference
  source: codex
  bridged: 2026-07-15
  tags: [gpu-offload, openfoam, performance, cfd]
---

OpenFOAM with VOF/MULES/PIMPLE is CPU-bound; GPU acceleration (via PETSc/AmgX) requires an explicit bridge that may not exist in the solver. Idle RTX 3090s at default P8/420W limits are not a path to speedup without architecture changes. Benchmark CPU-only performance first before committing to GPU strategy.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
