---
name: crossprovider codex safe-cron-process-group-termination
description: Safe cron process group termination
metadata:
  type: reference
  source: codex
  bridged: 2026-07-12
  tags: [operations, safety, process-management]
---

Terminate long-running cron jobs by signaling isolated PGID (`kill -TERM -- -<pgid>`), not cron daemon. Recheck before escalation to SIGKILL.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
