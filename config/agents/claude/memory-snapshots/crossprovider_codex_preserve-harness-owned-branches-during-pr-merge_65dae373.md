---
name: crossprovider codex preserve-harness-owned-branches-during-pr-merge
description: Preserve harness-owned branches during PR merge
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [git, merge-workflow, branch-preservation]
---

When merging a PR whose branch is owned by a harness or agent, use `git merge` without `--delete-branch` to preserve the branch for post-merge cleanup audits and worktree state inspection.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
