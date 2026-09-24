---
name: crossprovider codex gpu-cfd-infrastructure-baseline-gpu-claw
description: GPU/CFD infrastructure baseline (gpu-claw)
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [gpu-infrastructure, openfoam, cfd-baseline]
---

gpu-claw: dedicated CFD node with 2× RTX 3090 running OpenFOAM CPU/MPI-bound at 8 ranks. GPU offload not currently worthwhile (no PETSc/AmgX bridge); no historical evidence of clock locking or power-limit tuning. Frozen ace-win-1 heartbeat is canonical running signature; direct SSH timeouts are common.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
