---
name: crossprovider codex github-approval-labels-diverge-from-local-approv
description: GitHub approval labels diverge from local approval markers
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [plan-consistency, approval-gates]
---

`status:plan-approved` label on GitHub can exist without local `.planning/plan-approved/NNNN.md` file. Local markers are the source of truth for worktree execution; GitHub label alone does not permit implementation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
