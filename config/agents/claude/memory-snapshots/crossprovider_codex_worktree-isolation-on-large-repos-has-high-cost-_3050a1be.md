---
name: crossprovider codex worktree-isolation-on-large-repos-has-high-cost-
description: Worktree isolation on large repos has high cost and timeout risk
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [multi-agent, worktree-isolation, git-performance]
---

Creating a worktree with `isolation: worktree` on large repos (workspace-hub: ~33K files) triggers a full checkout and has ~60% timeout risk. Reserve worktree isolation for commit/push agents where it's mandatory; use in-process isolation or narrower operations for general multi-agent work on large repos.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
