---
name: crossprovider codex read-staged-artifacts-via-git-index-on-large-rep
description: Read staged artifacts via git index on large repos
metadata:
  type: reference
  source: codex
  bridged: 2026-06-18
  tags: [code-review, git-workflow, large-repos]
---

Use `git show :path` to read staged blobs directly from the index rather than working tree to avoid unstaged-change interference. On large repos where `git status` times out, use narrower commands like `git diff --cached` instead of full worktree walks.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
