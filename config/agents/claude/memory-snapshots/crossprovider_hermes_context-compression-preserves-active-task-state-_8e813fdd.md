---
name: crossprovider hermes context-compression-preserves-active-task-state-
description: Context compression preserves active task state across compaction boundaries
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [context-management, task-state, compression]
---

After context memory is compressed, active task lists, goals, and constraints survive and are restored. Detailed turn history is lost but can be inferred from goal/constraint context. Always verify assumptions against current file state and refetch live data before acting on recovered task state.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
