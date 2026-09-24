---
name: crossprovider codex gh-pr-diff-enables-read-only-review-without-work
description: gh pr diff enables read-only review without worktree recreation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [read-only-review, worktree-avoidance]
---

`gh pr diff <PR#>` provides the same diff surface for verification when local worktrees are unavailable or contended, avoiding lock contention and enabling parallel cleanup. Read-only reviews can skip worktree checkout.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
