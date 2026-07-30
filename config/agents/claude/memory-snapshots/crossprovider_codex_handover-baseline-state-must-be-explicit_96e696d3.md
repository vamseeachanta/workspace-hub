---
name: crossprovider codex handover-baseline-state-must-be-explicit
description: Handover baseline state must be explicit
metadata:
  type: reference
  source: codex
  bridged: 2026-07-18
  tags: [handover, clarity, coordination]
---

Always declare exact repo/branch/PR state in a handover (e.g., 'main at E2, #1037 not merged'). Omission sends downstream agents chasing stale assumptions about what's current vs. pending.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
