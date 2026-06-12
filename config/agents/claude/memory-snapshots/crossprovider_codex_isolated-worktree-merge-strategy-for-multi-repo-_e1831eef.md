---
name: crossprovider codex isolated-worktree-merge-strategy-for-multi-repo-
description: Isolated worktree merge strategy for multi-repo conflicts
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [git, workflow, multi-repo, merge-strategy]
---

When facing broad multi-repo conflicts (submodules, skills, config) across parallel work, use `git merge -s ours` in an isolated worktree to preserve main-branch content while accepting merge history. Avoids contaminating active workspace with partial conflict state or unintended submodule pointer changes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
