---
name: crossprovider codex git-worktree-metadata-corruption-fallback-to-can
description: Git worktree metadata corruption: fallback to canonical checkout
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-worktree, safety-fallback]
---

When a planned isolated worktree becomes unregistered by git (no `.git`, no file inventory) mid-session, the canonical main checkout is the safer fallback rather than trying to salvage the orphaned path. Orphaned worktree directories should be flagged as cleanup residue.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
