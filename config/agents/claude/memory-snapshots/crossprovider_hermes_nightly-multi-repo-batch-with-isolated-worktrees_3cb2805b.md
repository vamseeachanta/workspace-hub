---
name: crossprovider hermes nightly-multi-repo-batch-with-isolated-worktrees
description: Nightly multi-repo batch with isolated worktrees reduces contention
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-workflow, parallel-execution, worktree, nightly-batch]
---

Parallel execution across repos (assethold, worldenergydata, workspace-hub) using separate worktrees per lane + dedicated planning worktree avoids git-lock races and staged-change bleedthrough. Pattern: execution lanes remain independent, planning lane serializes shared-document edits to prevent manifest conflicts.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
