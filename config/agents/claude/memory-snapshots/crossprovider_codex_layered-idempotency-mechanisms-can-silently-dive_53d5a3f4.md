---
name: crossprovider codex layered-idempotency-mechanisms-can-silently-dive
description: Layered idempotency mechanisms can silently diverge and cause data loss
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [idempotency, state-machine, data-integrity]
---

When two independent dedup mechanisms (e.g., label-swap + per-message key) operate on the same flow, they can disagree: message sent but label not swapped → retry suppresses send while state shows unsent; or label swapped before send commits → silent drop. Requires explicit ordered state machine with atomic transitions and recovery paths, not independent idempotency layers.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
