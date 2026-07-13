---
name: crossprovider codex cron-configuration-duplication-may-coexist-with-
description: Cron configuration duplication may coexist with live processes
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [cron, audit, process-lifecycle]
---

Duplicate crontab entries (two `30 4 * * * ...` rows) can both be live; the presence of one does not make the other automatically stale. Audit process table AND schedule file together: identify which crontab line spawned which PID, and whether any process has outlived multiple schedule intervals (indicating it stalled or retried).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
