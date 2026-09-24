---
name: crossprovider codex hermes-kanban-blocked-task-rerun-is-not-idempote
description: Hermes kanban blocked-task rerun is not idempotent
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [hermes, kanban, idempotence, operational-hazard]
---

hermes kanban block <id> appends BLOCKED comment before status check; for already-blocked tasks, CLI fails silently after comment (no sticky-blocked event). Batch re-runs are not idempotent; tests mock the failure.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
