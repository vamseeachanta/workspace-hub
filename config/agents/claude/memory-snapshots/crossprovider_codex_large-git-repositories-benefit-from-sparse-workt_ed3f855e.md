---
name: crossprovider codex large-git-repositories-benefit-from-sparse-workt
description: Large Git repositories benefit from sparse worktrees for parallel work
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [performance, git-workflow, infrastructure]
---

Full checkout of 23k-file repos is prohibitively slow (~hours); sparse worktree containing only config/tests/dependencies is faster and prevents cross-branch contamination.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
