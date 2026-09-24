---
name: crossprovider codex stale-cron-overlaps-are-detectable-via-process-t
description: Stale cron overlaps are detectable via process tree and schedule config
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cron-debugging, process-lifecycle, schedule-config]
---

Multiple instances of the same scheduled job can run concurrently when prior instances exceed the schedule interval. Detect via process ancestry (parent cron PID) + timestamp comparison. Canonical source is scheduled-tasks YAML + renderer script; use both to identify stale vs. active copies.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
