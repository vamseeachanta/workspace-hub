---
name: crossprovider hermes task-state-lost-across-context-compression
description: Task state lost across context compression
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [context-compression, task-management, github-workflow]
---

in_progress tasks preserved in task list but execution context (current branch, generated artifacts, staged changes, test results) not tracked. Use explicit GitHub issue checkpoint comments before compression triggers to record state.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
