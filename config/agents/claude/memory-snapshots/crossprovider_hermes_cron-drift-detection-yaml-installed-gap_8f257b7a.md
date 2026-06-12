---
name: crossprovider hermes cron-drift-detection-yaml-installed-gap
description: Cron drift detection: YAML→installed gap
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [cron, drift, canonical-source, validation]
---

Canonical source config/scheduled-tasks/schedule-tasks.yaml can drift from installed crontab when setup-cron.sh --replace isn't re-run after YAML changes. On ace-linux-1, YAML had 34 tasks but live crontab (generated 2026-04-06) has only 28; missing entries include cron-health, queue-refresh-weekly, compliance tasks. Live crontab is not authoritative proof of current schedule—validate by comparing `setup-cron.sh --dry-run` output to `crontab -l`.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
