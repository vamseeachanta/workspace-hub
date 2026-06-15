---
name: crossprovider codex branch-pruning-requires-containment-verification
description: Branch pruning requires containment verification, not just gone upstream
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [branch-cleanup, git-refs, containment-check, stale-branch]
---

Local branches with `[gone]` upstream status are not automatically safe to prune. Verify containment in a known cleanup/preservation branch via `git rev-list --left-right --count origin/main...origin/cleanup-branch` before recommending deletion.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
