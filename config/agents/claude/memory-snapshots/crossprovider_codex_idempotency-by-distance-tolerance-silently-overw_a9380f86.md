---
name: crossprovider codex idempotency-by-distance-tolerance-silently-overw
description: Idempotency by distance tolerance silently overwrites distinct nearby values
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [deduplication, idempotency, tolerance-semantics]
---

Deduplication using distance-based tolerance (e.g., `< 0.5m`) instead of exact equality can overwrite distinct but nearby entries. Document whether idempotency means exact match or tolerance range; tests must verify the intended record is preserved, not just count.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
