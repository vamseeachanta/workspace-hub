---
name: crossprovider hermes cron-drift-causation-config-changes-don-t-auto-d
description: Cron drift causation: config changes don't auto-deploy to live crontab
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [cron, deployment, automation, drift]
---

Live crontab drifts when config/scheduled-tasks.yaml is updated but setup-cron.sh --replace is not re-run. Happened April 6→April 9: YAML has 32 tasks, live crontab stuck at 28. Recovery is deterministic: bash scripts/cron/setup-cron.sh --replace regenerates live crontab. Drift will recur if pattern repeats.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
