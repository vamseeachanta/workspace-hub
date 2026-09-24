---
name: crossprovider codex large-repo-sparse-worktree-index-refresh-is-the-
description: Large-repo sparse worktree: index refresh is the bottleneck
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-performance, sparse-worktree, large-repo]
---

When checking out planning-focused branches in 22K+ file repos, git index refresh (even for sparse materializations of ~235 files) is slower than the selected-content checkout. Move sparse worktrees to /tmp for local metadata; avoids repeated full-tree index walks in network-mounted directories.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
