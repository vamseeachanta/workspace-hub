---
name: crossprovider codex cherry-pick-for-partial-upstream-commits
description: Cherry-pick for partial upstream commits
metadata:
  type: reference
  source: codex
  bridged: 2026-07-29
  tags: [git, workflow]
---

When only one commit is needed from an upstream branch (e.g., a tested bugfix), cherry-pick that commit rather than rebasing the whole branch. Keeps branch based on origin/main without importing unrelated parents.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
