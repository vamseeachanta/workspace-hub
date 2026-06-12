---
name: crossprovider hermes worktree-isolation-costs-60-timeout-on-workspace
description: Worktree isolation costs 60% timeout on workspace-hub
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [worktree, performance, workspace-hub]
---

`isolation: worktree` on 33K-file repos materializes ~17–60 min. Reserve worktrees for commit/push agents only; use main checkout for planning/review.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
