---
name: crossprovider codex detect-parallel-worktree-collisions-via-git-stat
description: Detect parallel worktree collisions via git status before editing shared files
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, worktree, coordination]
---

When multiple agents work on the same feature branch in the same worktree, run git status first to detect other agents' untracked files and modifications. This session found untracked cores_density.py and modified test_cores_loader.py from parallel density work, preventing stomps. Check status before editing the same files.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
