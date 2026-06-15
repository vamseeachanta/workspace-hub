---
name: crossprovider codex git-status-timeouts-on-large-repos-timeout-confi
description: Git status timeouts on large repos; timeout config outside schedule YAML
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [timeout, performance, schedule-config, env-management]
---

git status --porcelain=v1 --untracked-files=all on workspace-hub/digitalmodel exceeds default PROBE_TIMEOUT_SEC=10. The live fix requires crontab env overrides (REPO_ECOSYSTEM_HYGIENE_PROBE_TIMEOUT_SEC=30), which live outside schedule-tasks.yaml. This decouples the declared schedule from runtime constraints; dry-run validation passes against YAML but live behavior differs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
