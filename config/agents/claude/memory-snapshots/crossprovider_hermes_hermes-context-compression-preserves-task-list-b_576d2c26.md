---
name: crossprovider hermes hermes-context-compression-preserves-task-list-b
description: Hermes context compression preserves task list but not live state
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [context-management, hermes-workflow, state-verification]
---

When a Hermes session resumes after compaction, the task list survives but 'completed actions' summary is stale. Always refetch live state (git status, gh issue view, filesystem probes) before trusting prior context; don't assume summary is current.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
