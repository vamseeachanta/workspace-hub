---
name: crossprovider codex scheduled-task-governance-requires-dual-registry
description: Scheduled-task governance requires dual-registry updates
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [governance, scheduled-tasks]
---

New scheduled tasks must be registered in both `config/scheduled-tasks/schedule-tasks.yaml` (machine-readable canonical schema) and `docs/ops/scheduled-tasks.md` (human-readable inventory). Acceptance criteria must require both updates or the inventory will drift.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
