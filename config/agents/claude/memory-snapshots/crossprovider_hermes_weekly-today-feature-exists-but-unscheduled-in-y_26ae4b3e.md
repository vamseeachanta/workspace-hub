---
name: crossprovider hermes weekly-today-feature-exists-but-unscheduled-in-y
description: Weekly today feature exists but unscheduled in YAML
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [cron, today-reports, scheduling, feature-gap]
---

daily_today.sh already supports --week flag and writes weekly summaries to logs/weekly/, but config/scheduled-tasks.yaml missing the weekly-today task definition. Example crontab.example still references the intended schedule (Monday 06:00). Feature can be restored by adding one YAML task entry without code changes.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
