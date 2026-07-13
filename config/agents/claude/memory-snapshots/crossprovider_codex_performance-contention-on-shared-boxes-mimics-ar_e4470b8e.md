---
name: crossprovider codex performance-contention-on-shared-boxes-mimics-ar
description: Performance contention on shared boxes mimics architectural bottlenecks
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [performance, mpi, contention-debugging, infrastructure]
---

Shared compute hosts (e.g., load spiking 7→24 during CFD runs) degrade MPI scaling even on CPU-efficient workloads. Dedicated quiet hardware eliminates contention jitter and restores predictable wall-clock behavior; this is separate from intrinsic algorithm efficiency.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
