---
name: crossprovider codex high-contention-git-repos-avoid-git-status-use-p
description: High-contention git repos: avoid git status, use plumbing
metadata:
  type: reference
  source: codex
  bridged: 2026-07-05
  tags: [git-performance, high-contention-repo, debugging]
---

When git status hangs, use git worktree list --porcelain, diff-index --cached, diff-files instead. PID scan via /proc more reliable than lock-file checks for detecting active processes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
