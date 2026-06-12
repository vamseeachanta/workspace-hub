---
name: crossprovider hermes verify-task-status-on-context-compacted-session-
description: Verify task status on context-compacted session resume
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [session-management, context-compaction, task-tracking]
---

When resuming sessions with context compaction + preserved task lists, the task state (in_progress/pending) can be stale — supporting context explaining what happened to that task was removed. Always verify task completion independently via git status / file inspection rather than trusting the preserved task status marker.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
