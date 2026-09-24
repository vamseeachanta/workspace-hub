---
name: crossprovider codex capacity-checks-must-account-for-live-load-not-j
description: Capacity checks must account for live load, not just total cores or averages
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [resource-allocation, scheduling]
---

Checking total cores (`cores`) or load averaging (`load1 / cores <= threshold`) masks current actual load. A host at load 11.9 with 8 cores can still be accepted if the check uses only total-core capacity. Capacity decisions must validate against live system state (e.g., `load1 + requested_ranks > cores`) before dispatch.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
