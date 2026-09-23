---
name: crossprovider codex dirty-tree-detection-tests-catch-uncommitted-wor
description: Dirty-tree detection tests catch uncommitted work in parallel sessions
metadata:
  type: reference
  source: codex
  bridged: 2026-07-30
  tags: [parallel-work, ci-correctness, git-state]
---

Tests like test_openfoam_batch_identity that explicitly fail on uncommitted src/ changes prevent silent CI bypasses when multiple agents work in the same worktree. Require clean tree verification before critical checks, especially in shared environments.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
