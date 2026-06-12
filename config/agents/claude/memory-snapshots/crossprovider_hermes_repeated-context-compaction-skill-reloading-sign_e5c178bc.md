---
name: crossprovider hermes repeated-context-compaction-skill-reloading-sign
description: Repeated context-compaction skill-reloading signals weak session handoff
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [harness-behavior, session-state, context-management]
---

Hermes #2760 sessions repeatedly started 'Loading skills...' despite prior turns already loading them, suggesting context compaction doesn't preserve executed-skills state. Active task list survives but skill state doesn't. Future sessions need to preserve [task_list, loaded_skills, execution_context] across compaction handoffs.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
