---
name: crossprovider codex merge-base-diff-catches-unintended-scope-creep
description: Merge-base diff catches unintended scope creep
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [diff-review, scope-control, git-workflow]
---

Compare working-tree changes to origin/main (merge-base) rather than making working-tree assumptions. Two-dot diffs can hide legacy file changes; explicit merge-base comparison reveals files that should not have been modified despite no explicit requirement to touch them.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
