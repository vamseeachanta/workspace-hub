---
name: crossprovider codex codex-worktree-git-metadata-requires-explicit-sa
description: Codex worktree git metadata requires explicit sandbox grant
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [codex, worktree, git-metadata, permissions, dispatch]
---

Codex agents dispatched to worktrees frequently encounter 'Read-only file system' on `git commit` even when working-tree file writes succeed. The `.git/worktrees/<name>/` metadata lives in the parent repo's `.git` directory and has separate permission scope in the sandbox. Initial state may be read-only; expect permission to be granted mid-session after deployment.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
