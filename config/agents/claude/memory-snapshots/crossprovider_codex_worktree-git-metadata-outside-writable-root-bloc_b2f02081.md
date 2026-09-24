---
name: crossprovider codex worktree-git-metadata-outside-writable-root-bloc
description: Worktree git metadata outside writable root blocks index operations
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-worktrees, sandbox, environmental-constraint]
---

When a git worktree's `.git` metadata lives outside the session's writable sandbox (e.g., `/mnt/.../worktrees/` while working in `/tmp/`), `git rm`, `git add`, and `git commit` fail with 'Unable to create index.lock: Read-only file system'. The worktree directory itself is writable, but Git metadata is not. Plan workflows that write index-free operations when worktree metadata is external.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
