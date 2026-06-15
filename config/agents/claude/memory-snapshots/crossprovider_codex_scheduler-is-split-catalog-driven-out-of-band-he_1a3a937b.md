---
name: crossprovider codex scheduler-is-split-catalog-driven-out-of-band-he
description: Scheduler is split: catalog-driven + out-of-band Hermes jobs
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [scheduler, automation, cron]
---

workspace-hub uses two scheduling planes. Standard crontab (38 cataloged lines) installs from config/scheduled-tasks/schedule-tasks.yaml via setup-cron.sh; Hermes maintains separate jobs (e.g., daily-cleanup at 23:00) not in YAML. Any audit or migration of scheduled tasks must account for both planes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
