---
name: crossprovider codex read-only-passes-should-not-clean-pre-existing-r
description: Read-only passes should not clean pre-existing residue in collaborative worktrees
metadata:
  type: reference
  source: codex
  bridged: 2026-07-08
  tags: [git-workflow, parallel-work, collaboration]
---

When conducting read-only source passes or code reviews in worktrees with parallel active work, observe but do not clean pre-existing residue (stash, cleanup-trash dirs, tmp files). Cleaning may interfere with parallel tasks and should only occur as explicit intent.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
