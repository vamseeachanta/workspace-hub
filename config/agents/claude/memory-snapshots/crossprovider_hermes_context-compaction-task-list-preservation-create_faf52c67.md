---
name: crossprovider hermes context-compaction-task-list-preservation-create
description: Context compaction + task list preservation creates stale handoff hazard
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, context-compaction, task-state, multi-agent]
---

Hermes sessions preserve task lists across context compaction but lose action details, causing later sessions to inherit 'in_progress' state without knowing whether tests passed, artifacts are stale, or code is ready. Leads to repeated work and false assumptions about completion. Recommend explicit status snapshot (test results, artifact timestamps, code diffs) in task descriptions before compaction.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
