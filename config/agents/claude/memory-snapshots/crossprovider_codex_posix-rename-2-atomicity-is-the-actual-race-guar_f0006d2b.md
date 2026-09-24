---
name: crossprovider codex posix-rename-2-atomicity-is-the-actual-race-guar
description: POSIX rename(2) atomicity is the actual race guard in bash claim patterns, not advisory locks
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [concurrency, atomic-operations, posix-guarantees, race-conditions, WRK-1049]
---

For concurrent claim/deduplication in bash, rely on POSIX rename(2) atomicity as the definitive race-breaker. Advisory session locks are useful audit trails and fast-fail checks, but they do not prevent two sessions from reaching a claim concurrently if mv fails after the pre-check. The second session's mv will fail atomically because the source is gone, which is the actual guard.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
