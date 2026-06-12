---
name: crossprovider hermes approval-markers-in-worktrees-enable-parallel-su
description: Approval markers in worktrees enable parallel sub-issue execution without re-gating
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [parallel-execution, workflow-pattern, approval-gating]
---

Pattern validated across parallel sessions: create `.planning/plan-approved/<N>.md` inside worktree before pushing to propagate umbrella approval to sub-issues without individual cross-review. Enables safe parallelization when parent issue is approved.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
