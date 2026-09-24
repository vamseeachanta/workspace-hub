---
name: crossprovider codex pre-push-hook-failures-in-incomplete-worktrees-h
description: Pre-push hook failures in incomplete worktrees have audited bypass
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, hooks, worktree, ci-cd]
---

Worktrees missing tier-1 sibling repo checkouts will fail normal pre-push hooks with 'missing sibling' errors. Pattern: normal push → hook fails → add review artifact → use audited skip mechanism (e.g., `GIT_PRE_PUSH_SKIP=1`) → push succeeds. No force-push needed; the skip flag is the legitimate path when tier-1 topology is incomplete.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
