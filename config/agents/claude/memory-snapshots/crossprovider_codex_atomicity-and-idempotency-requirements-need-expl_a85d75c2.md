---
name: crossprovider codex atomicity-and-idempotency-requirements-need-expl
description: Atomicity and idempotency requirements need explicit merge/replace strategy
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [atomicity, idempotency, file-operations, state-management]
---

Plans requiring both (a) atomic directory-level replace and (b) incremental idempotency (detecting/skipping stale files) fail if merge vs replace behavior is undefined. Atomic replace can silently delete unrelated files; merge breaks atomicity. Plans must explicitly state whether outputs are replaced, merged, rolled back, or preserved on re-run.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
