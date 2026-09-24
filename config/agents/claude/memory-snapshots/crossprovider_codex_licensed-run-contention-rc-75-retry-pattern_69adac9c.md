---
name: crossprovider codex licensed-run-contention-rc-75-retry-pattern
description: Licensed run contention: rc 75 retry pattern
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [licensing, queue, error-handling, retry]
---

When a licensed solver seat returns rc 75, the seat is contentious/locked. Retry by deleting the result JSON and resubmitting; seat serialization is enforced at the queue level. Frozen heartbeat (no update) on the execution host is the documented running signature.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
