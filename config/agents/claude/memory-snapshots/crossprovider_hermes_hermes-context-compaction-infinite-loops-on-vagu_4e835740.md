---
name: crossprovider hermes hermes-context-compaction-infinite-loops-on-vagu
description: Hermes context-compaction infinite loops on vague task statements
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, context-management, task-clarity]
---

Sessions with unclear active tasks (e.g., 'inspect OCIMF forces') enter state-loss loops: context summaries fail to preserve actionable state; agent restarts same inspection loop across 10+ sessions without progress. Clear, bounded task phrasing ('read files X, Y, Z; recommend routing structure') avoids this.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
