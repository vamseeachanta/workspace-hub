---
name: crossprovider codex licensed-solver-seats-are-serialized-rc-75-conte
description: Licensed solver seats are serialized; rc 75 = contention; delete result JSON to retry
metadata:
  type: reference
  source: codex
  bridged: 2026-07-15
  tags: [operations, licensing, solver]
---

Each licensed seat runs one job at a time (serialized). Return code 75 signals resource contention; retry by deleting the result JSON file. Monitor active runs via frozen heartbeat JSON file (check ~3 hours after seat claim).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
