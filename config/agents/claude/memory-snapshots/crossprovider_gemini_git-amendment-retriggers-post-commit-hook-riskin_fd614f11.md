---
name: crossprovider gemini git-amendment-retriggers-post-commit-hook-riskin
description: Git amendment retriggers post-commit hook, risking non-fast-forward errors
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [git-hooks, git-amend, edge-case, post-commit]
---

When a user runs `git commit --amend`, the post-commit hook fires again. If the original commit was already pushed and auto-push is enabled, amending and re-pushing will hit a non-fast-forward error. Detect amended commits or gracefully handle push failures to prevent user confusion.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
