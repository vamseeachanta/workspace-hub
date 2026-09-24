---
name: crossprovider codex github-connector-fallback-for-slow-local-git-met
description: GitHub connector fallback for slow local git metadata
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-performance, github-connector, worktree-contention]
---

When local git operations hang in contended workspaces (even read-only `git diff`), use GitHub connector to commit/push instead of waiting. Avoids blocking the lane on workspace contention.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
