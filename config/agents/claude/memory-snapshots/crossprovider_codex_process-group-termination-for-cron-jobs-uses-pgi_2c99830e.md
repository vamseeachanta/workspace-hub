---
name: crossprovider codex process-group-termination-for-cron-jobs-uses-pgi
description: Process group termination for cron jobs uses PGID, not daemon PGID
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [process-management, cron, signal-handling, safety]
---

Use `kill -TERM -- -<PGID>` to terminate isolated job process groups; never signal the cron daemon itself (PGID 1666). Prevents accidental scheduler shutdown during cleanup and enables bounded recheck before escalation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
