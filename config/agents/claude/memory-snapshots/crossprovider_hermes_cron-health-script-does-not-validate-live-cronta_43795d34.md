---
name: crossprovider hermes cron-health-script-does-not-validate-live-cronta
description: Cron-health script does not validate live crontab
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [cron-health, validation, limitations]
---

scripts/monitoring/cron-health-check.sh reads schedule-tasks.yaml and logs only; it explicitly does not inspect installed crontab. Reports can show 'MISSING' for tasks that are actually installed but have stale/empty logs. Do not rely on cron-health alone as proof of installation state; directly compare YAML to `crontab -l`.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
