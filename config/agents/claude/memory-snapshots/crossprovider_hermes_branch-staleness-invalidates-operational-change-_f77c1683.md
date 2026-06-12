---
name: crossprovider hermes branch-staleness-invalidates-operational-change-
description: Branch staleness invalidates operational-change verification claims
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-state, operational-changes, merge-readiness, branch-staleness]
---

Issue #2766 worktree was ahead 1, behind 16 commits versus main. For operational changes (repo normalization, machine placement), stale base means the verified state may diverge from main. Rebase/fast-forward to main before closeout to eliminate evidence of staleness.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
