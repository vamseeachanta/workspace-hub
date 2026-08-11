---
name: crossprovider codex verify-working-tree-state-before-adversarial-rev
description: Verify working-tree state before adversarial review measurements
metadata:
  type: reference
  source: codex
  bridged: 2026-08-10
  tags: [adversarial-review, code-review, verification-discipline]
---

Before accepting any measurements or code analysis in an adversarial review, confirm the actual checkout state (branch, commit, file modifications) matches the stated precondition. A dirty or differently-branched worktree invalidates measurement-dependent claims and can cause reviewers to accept regressions or false reassurances.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
