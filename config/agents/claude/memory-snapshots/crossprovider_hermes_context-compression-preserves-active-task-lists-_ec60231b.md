---
name: crossprovider hermes context-compression-preserves-active-task-lists-
description: Context compression preserves active task lists across windows
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [context-management, task-persistence, compression-handoff]
---

Long sessions (60+ messages compacted) maintain active task list metadata through compression checkpoints, enabling resumption in new context windows without losing in-progress work state. Task list format: `[status] t#. Description` with status codes (>, -, [ ]).

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
