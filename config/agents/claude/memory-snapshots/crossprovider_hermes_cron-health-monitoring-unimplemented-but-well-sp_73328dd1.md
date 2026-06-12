---
name: crossprovider hermes cron-health-monitoring-unimplemented-but-well-sp
description: Cron health monitoring unimplemented but well-specified
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [cron-monitoring, gap, specification]
---

Issue #1512 specifies need: read config/scheduled-tasks/schedule-tasks.yaml, check each job's last log timestamp, flag stale/missing runs, write JSON report to .claude/state/cron-health/. The spec is clear but implementation is incomplete. Blocker for cron reliability insights.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
