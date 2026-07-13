---
name: crossprovider codex linked-worktree-canonical-derivation-via-git-mar
description: Linked-worktree canonical derivation via .git marker
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [git-worktrees, testing, security]
---

Don't use active worktree path to identify canonical checkout; derive it via `.git` file marker + `commondir` attribute parsing. Tests must cover all three roots: active, canonical, and actual target. False-green occurs when test covers only active-worktree descendants.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
