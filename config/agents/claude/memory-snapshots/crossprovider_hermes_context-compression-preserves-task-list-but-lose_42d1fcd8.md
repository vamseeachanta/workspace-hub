---
name: crossprovider hermes context-compression-preserves-task-list-but-lose
description: Context compression preserves task list but loses exploration state
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes-agent, context-management, workflow-efficiency]
---

When Hermes sessions compress, TaskList survives but the agent replays 'intake/gather intelligence' steps already explored in prior context windows. Compaction summary lacks exploration details, causing inefficient re-work. Include a summarized 'already explored' section in compaction to prevent replay.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
