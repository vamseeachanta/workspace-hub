---
name: crossprovider codex multiple-idempotency-layers-must-compose-via-ord
description: Multiple idempotency layers must compose via ordered state machine, not independently
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [idempotency, state-machine, coordination]
---

When dedup mechanisms coexist (e.g., GitHub label-swap + per-message idempotency key), they can disagree and either double-send or drop. Requires single state machine with recovery rules, not loose composition of independent checks.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
