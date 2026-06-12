---
name: crossprovider codex stash-bookkeeping-must-verify-git-stash-success
description: Stash bookkeeping must verify git stash success
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [git-workaround, state-tracking]
---

Failed `git stash push` must not set `stashed=True` flag; later code pops the top stash entry without knowing who created it, potentially losing unrelated work. Always check push success before marking for restoration.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
