---
name: crossprovider codex lease-idempotency-tracking-is-better-than-commen
description: Lease/idempotency tracking is better than comment-only job tracking
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [distributed-systems, architecture-pattern]
---

Multi-machine dispatch systems need a structured lease ledger (TTL, idempotency keys, leader-host locking) rather than comment-based or Git-file-only job state. Existing patterns in provider-dispatch-loop.py show this is viable; new work should reuse or factor this rather than invent weaker alternatives.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
