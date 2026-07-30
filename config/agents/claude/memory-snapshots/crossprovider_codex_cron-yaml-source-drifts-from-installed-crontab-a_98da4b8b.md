---
name: crossprovider codex cron-yaml-source-drifts-from-installed-crontab-a
description: Cron YAML source drifts from installed crontab and needs automation
metadata:
  type: reference
  source: codex
  bridged: 2026-07-13
  tags: [cron, infrastructure, automation, source-of-truth]
---

The workspace maintains cron schedules in config/scheduled-tasks/schedule-tasks.yaml (canonical source), but installed crontab diverges: cadence changes (Hermes bridge 04:20 → 04:25), command flags dropped (--commit), and log paths mismatch (repository-sync declared in YAML vs actual). Without automated health monitoring, overlapping instances accumulate (three concurrent repo-sync runs observed), risking Git/state corruption.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
