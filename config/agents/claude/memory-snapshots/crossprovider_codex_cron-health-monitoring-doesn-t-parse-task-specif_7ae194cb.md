---
name: crossprovider codex cron-health-monitoring-doesn-t-parse-task-specif
description: Cron health monitoring doesn't parse task-specific status
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [cron, monitoring]
---

cron-health-check.sh:83-92 scans only generic log error tokens (ERROR, FAIL, etc.) and does not interpret structured status lines like 'task=repo-ecosystem-hygiene status=ERROR'. Task-specific failure modes are invisible to health checks.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
