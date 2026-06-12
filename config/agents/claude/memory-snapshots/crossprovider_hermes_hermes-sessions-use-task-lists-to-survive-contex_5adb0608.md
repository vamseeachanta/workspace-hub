---
name: crossprovider hermes hermes-sessions-use-task-lists-to-survive-contex
description: Hermes sessions use task lists to survive context compaction
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, context-management, tool-pattern]
---

Hermes compaction drops up to 200+ messages but preserves task lists across compression boundaries via `[Your active task list was preserved...]`. Agents resume work by reading task status and continuing from in_progress/pending items rather than replaying lost context.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
