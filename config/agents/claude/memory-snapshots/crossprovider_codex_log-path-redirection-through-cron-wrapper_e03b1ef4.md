---
name: crossprovider codex log-path-redirection-through-cron-wrapper
description: Log path redirection through cron wrapper
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [log-monitoring, wrapper-behavior, cron-configuration]
---

Scheduled tasks may redirect logs through a $LOG wrapper variable (e.g., cron-wrapper.log) even though schedule-tasks.yaml advertises specific log patterns (e.g., logs/repository-sync-*.log). Log freshness inference must account for this indirection rather than assuming the declared path is the actual destination.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
