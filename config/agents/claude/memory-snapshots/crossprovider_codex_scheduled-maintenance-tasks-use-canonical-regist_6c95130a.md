---
name: crossprovider codex scheduled-maintenance-tasks-use-canonical-regist
description: Scheduled maintenance tasks use canonical registry with tests and docs
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [automation, scheduled-tasks, infrastructure]
---

Security and maintenance tasks should be registered in config/scheduled-tasks/schedule-tasks.yaml (with schema: id, schedule/cron, machines, requires, command, log) and documented in docs/ops/scheduled-tasks.md. Reference existing scripts like secrets-scan.sh for structure (set -euo pipefail, REPO_ROOT, arg parsing). Create tests/ counterparts for verification.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
