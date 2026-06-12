---
name: crossprovider hermes canonical-source-config-scheduled-tasks-schedule
description: Canonical source: config/scheduled-tasks/schedule-tasks.yaml is single source of truth
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [canonical-source, documentation, hierarchy]
---

YAML header states this explicitly. All cron/task-scheduler entries must be declared there. setup-cron.sh reads and generates crontab from it. docs/ops/scheduled-tasks.md is documentation inventory (may be incomplete/stale), not authoritative for exact current installed state. For claims about what is scheduled, cite YAML + validated live crontab, not docs.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
