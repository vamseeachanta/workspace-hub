---
name: crossprovider hermes hermes-context-compression-loses-task-continuity
description: Hermes context compression loses task continuity when summaries are incomplete
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, context-management, session-handoff, task-tracking]
---

Multiple sessions show 'Summary generation was unavailable' with 20+ messages dropped, leaving incomplete task handoffs. Hermes loops on same work (SIROCCO TDD) across sessions without clear progression. Mitigate by posting GitHub issue comments as task checkpoints instead of relying solely on context-window summaries.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
