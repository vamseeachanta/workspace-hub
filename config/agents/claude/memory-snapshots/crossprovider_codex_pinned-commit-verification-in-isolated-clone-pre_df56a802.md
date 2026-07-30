---
name: crossprovider codex pinned-commit-verification-in-isolated-clone-pre
description: Pinned-commit verification in isolated clone prevents concurrent-activity contamination
metadata:
  type: reference
  source: codex
  bridged: 2026-07-15
  tags: [git-review, isolation, concurrent-safety]
---

Review shared worktrees using git show <commit>: to pin reads and avoid mutable HEAD changing mid-review. Run verification in isolated temporary clones when the review depends on index state (e.g., staged blobs).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
