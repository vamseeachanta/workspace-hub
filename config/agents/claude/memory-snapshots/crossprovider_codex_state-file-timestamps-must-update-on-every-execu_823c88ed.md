---
name: crossprovider codex state-file-timestamps-must-update-on-every-execu
description: State file timestamps must update on every execution, not just on changes
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [state-tracking, observability, cron-jobs, idempotency]
---

When tracking last-execution time in a state file (e.g., last_scan_at), update the timestamp even when the primary condition (version change, new data, etc.) does not fire. Otherwise the state file becomes stale and you lose observability into whether the job is running or has stopped running.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
