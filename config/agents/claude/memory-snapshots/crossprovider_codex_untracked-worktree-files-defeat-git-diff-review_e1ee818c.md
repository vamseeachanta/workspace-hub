---
name: crossprovider codex untracked-worktree-files-defeat-git-diff-review
description: Untracked worktree files defeat git diff review
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [review, git, worktree, tooling-quirks]
---

When implementation files are untracked (e.g., new files in a worktree), `git diff` produces empty output; reviews must inspect files directly and explicitly call out that no three-dot diff is available. This affects risk assessment when files haven't been staged yet.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
