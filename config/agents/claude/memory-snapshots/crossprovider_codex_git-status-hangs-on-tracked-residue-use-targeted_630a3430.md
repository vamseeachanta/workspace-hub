---
name: crossprovider codex git-status-hangs-on-tracked-residue-use-targeted
description: git status hangs on tracked residue; use targeted plumbing
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-performance, ci-timeout, worktree-management]
---

Broad `git status` times out in repos with tracked FUSE-hidden files. Use targeted queries: `git ls-files`, `git rev-parse HEAD`, `git merge-base`, `git diff HEAD -- <path>`. Avoids index locks and filesystem exhaustion.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
