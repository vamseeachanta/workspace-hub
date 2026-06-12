---
name: crossprovider hermes large-repo-parallel-agents-require-git-tracked-t
description: Large-repo parallel agents require git-tracked task preservation
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [agent-workflow, context-compression, task-persistence, large-repo]
---

Multi-session work on workspace-hub (33K files) with mandatory context compression across 13+ handoffs requires task lists and plan markers persisted to git to survive session resets; ephemeral `.planning/` directories lost on context boundaries.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
