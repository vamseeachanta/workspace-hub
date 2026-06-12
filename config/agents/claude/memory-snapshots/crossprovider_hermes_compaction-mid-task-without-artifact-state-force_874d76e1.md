---
name: crossprovider hermes compaction-mid-task-without-artifact-state-force
description: Compaction mid-task without artifact state forces re-entry
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [context-management, multi-session-state]
---

Multiple context compactions on the same 'in_progress' task caused future sessions to lose the thread and restart discovery. Task list persisted unchanged (intake → draft → review → post) across ~11 sessions but lacked intermediate files marking progress. Intermediate artifacts (explicit plan file, draft issue body, review results) serve as ground truth across context resets and prevent restart loops.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
