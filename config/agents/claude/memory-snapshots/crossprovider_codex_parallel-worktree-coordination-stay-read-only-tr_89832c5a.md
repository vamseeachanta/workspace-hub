---
name: crossprovider codex parallel-worktree-coordination-stay-read-only-tr
description: Parallel-worktree coordination: stay read-only, treat untracked artifacts as off-limits
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [coordination, worktree, parallel-work, safety]
---

When multiple review/verification processes share a worktree, Codex stays strictly read-only and treats untracked review artifacts from parallel sessions as off-limits without independent verification. Derive evidence only from committed diff and tracked files. Prevents write conflicts and polluted shared state.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
