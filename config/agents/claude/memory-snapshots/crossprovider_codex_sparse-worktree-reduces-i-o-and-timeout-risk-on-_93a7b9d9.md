---
name: crossprovider codex sparse-worktree-reduces-i-o-and-timeout-risk-on-
description: Sparse worktree reduces I/O and timeout risk on large monorepos
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [monorepo-performance, worktree-isolation, filesystem-tuning]
---

Full isolated checkout of large repos (33K+ files) has 60% timeout risk on slow filesystems. Sparse checkout materializing only documentation paths for standards discovery reduced scope to relevant subtree, eliminating contention and avoiding file-system scan timeouts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
