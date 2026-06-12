---
name: crossprovider codex shared-worktree-git-contention-blocks-metadata-o
description: Shared worktree git contention blocks metadata operations
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [git-contention, workspace-hub-shared, parallel-agents]
---

Plain `git status`, `git log`, `git diff`, and `git commit` hang 10-30s+ when multiple agents hit the shared workspace-hub checkout concurrently. Workaround: bounded timeouts on individual commands, read `.git/` pointers directly, use GitHub API/refs, or use path-scoped `git <cmd> -- <path>` instead of broad queries. Prefer `gh` CLI over local git during high parallel load.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
