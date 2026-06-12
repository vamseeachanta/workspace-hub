---
name: crossprovider hermes context-compaction-preserves-task-lists-but-lose
description: Context compaction preserves task lists but loses implementation context
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [context-management, compression, task-preservation]
---

When Hermes agent sessions hit ~20+ message removal, compaction preserves task state (e.g., e1–e6 stages) but erases reasoning/intermediate findings; resuming requires reading compaction summaries and re-inspecting working files to recover implementation direction.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
