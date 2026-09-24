---
name: crossprovider codex cron-command-log-family-parity-requirement
description: Cron command/log-family parity requirement
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cron-tooling, log-management, task-monitoring]
---

setup-cron.sh installs only task.command, not task.log declaration. cron-health-check.sh reads task.log patterns to determine what file to monitor. Commands must redirect output to the exact log path family declared in schedule-tasks.yaml or cron-health won't detect task status.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
