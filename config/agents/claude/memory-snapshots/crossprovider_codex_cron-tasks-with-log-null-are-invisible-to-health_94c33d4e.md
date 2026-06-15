---
name: crossprovider codex cron-tasks-with-log-null-are-invisible-to-health
description: Cron tasks with log:null are invisible to health monitoring
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [cron, monitoring, task-design, logging]
---

cron-health-check.sh skips any scheduled task with log: null. If a task requires health monitoring, it must declare a concrete log path or glob. Tasks without logs cannot be monitored by cron-health.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
