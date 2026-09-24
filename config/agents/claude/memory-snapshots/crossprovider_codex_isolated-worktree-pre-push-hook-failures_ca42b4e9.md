---
name: crossprovider codex isolated-worktree-pre-push-hook-failures
description: Isolated worktree pre-push hook failures
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, hooks, worktree-isolation, sibling-repos]
---

When using `isolation: worktree` in a monorepo with sibling-repo checks, pre-push hooks can fail because sibling directories are not checked out in the isolated worktree. Capture exact hook output before deciding whether to bypass; the hook failure is the evidence needed to resolve the blocker, not cause to skip verification.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
