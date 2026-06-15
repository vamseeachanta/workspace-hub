---
name: crossprovider codex git-sandbox-blocks-worktree-metadata-operations
description: Git sandbox blocks worktree metadata operations
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [git, sandbox, worktree, blocker]
---

`git add`, `git rm`, `git commit` fail in worktrees under `/tmp/` because `.git/worktrees/` metadata lives at `/mnt/...` (outside writable sandbox), causing 'Unable to create index.lock' errors. No fallback to plain `rm` is acceptable since verification depends on git index mutation. This is a hard blocker for cleanup/commit in temporary worktrees.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
