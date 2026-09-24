---
name: crossprovider codex worktree-drift-breaks-review-reads-pin-to-commit
description: Worktree drift breaks review reads; pin to commit SHA instead
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [code-review, git, worktree-isolation, ci-cd]
---

When reviewing a PR at an explicit commit SHA while the worktree is checked out to a different HEAD (or has drifted), filesystem reads return stale content from the wrong commit. Instead, read diffs via `git diff BASE..HEAD` and file blobs via `git show SHA:path` to ensure all review evidence is pinned to the correct commits.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
