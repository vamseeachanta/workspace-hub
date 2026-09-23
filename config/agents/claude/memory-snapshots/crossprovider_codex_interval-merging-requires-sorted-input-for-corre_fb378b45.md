---
name: crossprovider codex interval-merging-requires-sorted-input-for-corre
description: Interval merging requires sorted input for correctness
metadata:
  type: reference
  source: codex
  bridged: 2026-07-29
  tags: [correctness, intervals, rig-days]
---

WAR rows must be sorted chronologically before adjacency/gap checks; unsorted identical input produced order-dependent wrong answers (14 days vs 366 days). Apply to any interval-merging or NPT-gap logic.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
