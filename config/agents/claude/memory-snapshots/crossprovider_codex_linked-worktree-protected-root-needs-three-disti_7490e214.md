---
name: crossprovider codex linked-worktree-protected-root-needs-three-disti
description: Linked-worktree protected-root needs three distinct paths
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-worktrees, path-validation, linked-worktrees]
---

Protected-root checks in linked-worktree environments must separately validate active worktree, canonical checkout (derived from `.git` marker's commondir), and actual target location. A schema-local Git-layout helper can derive these without external imports.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
