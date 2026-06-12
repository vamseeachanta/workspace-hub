---
name: crossprovider codex scheduled-tasks-need-dual-registry-yaml-human-do
description: Scheduled tasks need dual registry (YAML + human docs)
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [operations, automation, documentation]
---

config/scheduled-tasks/schedule-tasks.yaml is machine-readable; docs/ops/scheduled-tasks.md is human-readable. Both must be kept in sync. Missing either one breaks usability (automation fails to find tasks, or humans don't know what is scheduled). Treat as a single 2-file deliverable.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
