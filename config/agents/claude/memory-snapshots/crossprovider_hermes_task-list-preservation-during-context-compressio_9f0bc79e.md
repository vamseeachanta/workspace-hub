---
name: crossprovider hermes task-list-preservation-during-context-compressio
description: Task list preservation during context compression enables workflow resumption
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [context-compression, harness-behavior, workflow-resume]
---

When Hermes context fills and messages are compacted, the harness preserves active task lists as structured YAML/JSON artifacts (e.g., `[>] draft. Draft canonical plan...`). This allows resumed execution of multi-step workflows without user re-invocation, treating the task list as a continuation checkpoint.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
