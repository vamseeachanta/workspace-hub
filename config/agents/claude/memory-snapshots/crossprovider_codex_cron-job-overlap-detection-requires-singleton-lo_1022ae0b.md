---
name: crossprovider codex cron-job-overlap-detection-requires-singleton-lo
description: Cron job overlap detection requires singleton locking
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cron, concurrency, scheduling, locking]
---

Long-running scheduled jobs need per-task max_runtime_seconds, overlap detection by task ID/process group, and mutex locking for mutating jobs. Prevents concurrent state corruption and resource exhaustion from duplicate runs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
