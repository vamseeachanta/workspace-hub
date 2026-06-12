---
name: crossprovider hermes cron-drift-from-asynchronous-schedule-updates
description: Cron drift from asynchronous schedule updates
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [cron-ops, config-drift, schedule-sync]
---

Live crontab becomes stale when schedule-tasks.yaml is updated but setup-cron.sh --replace is not re-run. Root cause: install script uses generated timestamp; YAML changes don't trigger reinstall. Parity must be verified by comparing dry-run output to live crontab.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
