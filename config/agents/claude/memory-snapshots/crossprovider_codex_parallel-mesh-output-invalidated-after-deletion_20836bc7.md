---
name: crossprovider codex parallel-mesh-output-invalidated-after-deletion
description: Parallel mesh output invalidated after deletion
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [mesh-validation, MPI, CFD, architectural-hazard]
---

MPI mesh output stored in processor trees becomes inaccessible after deletion; mesh validation must use explicit reconstruction step or per-processor comparison before cleanup to verify correctness.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
