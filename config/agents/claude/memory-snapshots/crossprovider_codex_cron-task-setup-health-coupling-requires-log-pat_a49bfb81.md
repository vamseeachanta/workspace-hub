---
name: crossprovider codex cron-task-setup-health-coupling-requires-log-pat
description: Cron task setup/health coupling requires log path alignment
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [cron, observability, infrastructure]
---

setup-cron.sh installs only task.command while cron-health-check.sh scans task.log. The command must redirect to the exact log path declared in schedule-tasks.yaml's log: field, or health checks will miss the real output. Repository-sync uses $LOG indirection, creating ambiguity—cron-health remains source of truth for freshness, not log timestamp inference.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
