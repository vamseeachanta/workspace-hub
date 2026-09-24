---
name: crossprovider codex commit-pinning-via-isolated-clones-prevents-revi
description: Commit pinning via isolated clones prevents review contamination in concurrent worktrees
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-workflow, review-isolation, concurrent-safety, reproducibility]
---

When reviewing in a shared worktree with concurrent activity, pin all diffs and reads to an explicit commit hash using an isolated temporary clone. This prevents HEAD-mutable shared worktree state from contaminating the review snapshot while other sessions modify the branch.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
