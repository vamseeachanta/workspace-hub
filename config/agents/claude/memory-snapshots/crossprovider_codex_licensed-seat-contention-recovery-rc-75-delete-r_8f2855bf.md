---
name: crossprovider codex licensed-seat-contention-recovery-rc-75-delete-r
description: Licensed-seat contention recovery: rc=75, delete result JSON and retry
metadata:
  type: reference
  source: codex
  bridged: 2026-07-15
  tags: [licensed-runs, queue, aqwa, retry-pattern]
---

AQWA/OrcaWave seat serialization contention surfaces as rc=75. Recovery mechanic: delete the stale result JSON and requeue. No retry-logic needed; seat becomes available immediately.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
