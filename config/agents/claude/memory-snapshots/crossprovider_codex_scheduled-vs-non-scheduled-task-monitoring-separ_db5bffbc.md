---
name: crossprovider codex scheduled-vs-non-scheduled-task-monitoring-separ
description: Scheduled vs non-scheduled task monitoring separation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [task-monitoring, cron-health, architecture]
---

Tasks not defined in schedule-tasks.yaml (like daily-cleanup) cannot be reported via cron-health and should be linked as issue/runbook context instead. This clarifies monitoring boundaries and prevents false status inferences.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
