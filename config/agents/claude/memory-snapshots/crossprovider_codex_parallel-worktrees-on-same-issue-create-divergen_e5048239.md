---
name: crossprovider codex parallel-worktrees-on-same-issue-create-divergen
description: Parallel worktrees on same issue create divergent lanes—preserve authoritatively
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [parallel-work, worktree-hygiene, branch-archaeology]
---

When multiple worktrees exist for one issue, branches diverge. Identify the authoritative lane (pushed remote HEAD, clean worktree, passing tests), preserve others without cleanup. Codex #166 example: older loop branch was ancestral but superseded; divergent `0f9bcaf` was non-authoritative but belonged to other sessions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
