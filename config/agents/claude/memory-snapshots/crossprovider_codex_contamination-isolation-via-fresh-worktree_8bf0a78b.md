---
name: crossprovider codex contamination-isolation-via-fresh-worktree
description: Contamination isolation via fresh worktree
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [concurrent-work, worktree-isolation]
---

When parallel writers contaminate an isolated worktree, freeze writes, preserve the collision diff, treat committed HEAD as authoritative, and create a new clean worktree for repairs. This prevents code pollution while preserving evidence.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
