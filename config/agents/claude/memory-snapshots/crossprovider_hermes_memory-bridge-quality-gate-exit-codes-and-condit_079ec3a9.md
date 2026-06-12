---
name: crossprovider hermes memory-bridge-quality-gate-exit-codes-and-condit
description: Memory bridge quality gate: exit codes and conditional compaction
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [memory-quality-gate, hermes]
---

`check-memory-drift.sh` exit 0 = in-sync (skip bridge); exit 1 = drift. Pre-bridge-quality.sh scores memory: <50 aborts, 50-70 auto-compacts then bridges, >=70 bridges directly. Gates degraded memory from cross-provider stores.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
