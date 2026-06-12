---
name: crossprovider hermes hermes-context-compaction-loses-task-momentum
description: Hermes context compaction loses task momentum
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, context-management, handoff]
---

When Hermes context compacts, preserved task lists (marked in_progress) don't carry enough implementation detail; agents restart discovery loops instead of resuming. Task status alone is insufficient for resuming work across compression boundaries.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
