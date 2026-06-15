---
name: crossprovider codex log-location-drifts-from-schedule-tasks-yaml-dec
description: Log location drifts from schedule-tasks.yaml declarations
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [monitoring, log-paths, audit]
---

config/scheduled-tasks/schedule-tasks.yaml advertises log paths (e.g., logs/repository-sync-*.log), but cron wrappers may redirect via $LOG to logs/quality/cron-wrapper.log. Log-based freshness audits are unreliable; use cron-health-check.sh as the authoritative source.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
