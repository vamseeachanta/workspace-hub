---
name: crossprovider hermes context-compaction-loses-task-continuity-for-mul
description: Context compaction loses task continuity for multi-turn work
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [context, continuation, workflow]
---

When conversation context is compressed mid-task, prior task state, inferred goals, and decision context are lost. Sessions must infer task continuation from workspace state alone, which is fragile. When resuming compacted work, explicitly verify the inferred task before proceeding.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
