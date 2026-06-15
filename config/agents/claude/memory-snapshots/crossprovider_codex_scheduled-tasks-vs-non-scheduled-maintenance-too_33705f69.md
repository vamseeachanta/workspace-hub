---
name: crossprovider codex scheduled-tasks-vs-non-scheduled-maintenance-too
description: Scheduled tasks vs. non-scheduled maintenance tools have different health models
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [cron, architecture, observability]
---

Only YAML-registered scheduled tasks appear in cron-health status. Tools like daily-cleanup.sh that aren't in schedule-tasks.yaml should link as issue/runbook context (#2752, #2652), not be folded into the cron health reporting model.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
