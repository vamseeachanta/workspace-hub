---
name: crossprovider codex two-phase-sampling-prevents-dominant-source-over
description: Two-phase sampling prevents dominant source overflow
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [sampling, pagination, algorithm]
---

When sampling bounded rows from uneven registries, emit deterministically one row per configured source first, then fill remaining slots in registry order. Prevents dense early sources from consuming all slots, ensuring later sources contribute.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
