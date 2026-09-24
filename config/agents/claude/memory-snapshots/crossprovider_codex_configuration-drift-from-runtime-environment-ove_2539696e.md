---
name: crossprovider codex configuration-drift-from-runtime-environment-ove
description: Configuration drift from runtime environment overrides
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [configuration-management, environment-variables, source-of-truth, drift]
---

Runtime timeout overrides and environment variables set in the live crontab don't flow back to `schedule-tasks.yaml`, the source of truth. This creates untestable state where dry-run validation differs from actual execution. Scheduled-task configuration must be complete in source YAML; runtime overrides risk configuration debt.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
