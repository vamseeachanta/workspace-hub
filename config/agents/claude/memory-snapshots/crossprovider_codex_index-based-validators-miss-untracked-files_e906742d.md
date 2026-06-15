---
name: crossprovider codex index-based-validators-miss-untracked-files
description: Index-based validators miss untracked files
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [git-validation, test-design, file-coverage]
---

Checkers that operate on staged git blobs (conflict-markers, etc.) miss working-tree and untracked files. Be explicit about staging dependency, or add a separate working-tree scan for new/modified files.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
