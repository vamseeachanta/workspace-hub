---
name: crossprovider hermes four-surface-inventory-mandatory-for-scheduler-p
description: Four-surface inventory mandatory for scheduler parity reports
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [scheduler, harness, requirements]
---

Scheduler/cron visibility requires coverage of all four surfaces: (1) `config/scheduled-tasks/schedule-tasks.yaml`, (2) `setup-cron.sh --dry-run` output, (3) live `crontab -l`, (4) `hermes cron list`. Treating any as optional conflicts with issue requirements and triggers reviewer MAJOR. Each surface must have explicit test coverage.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
