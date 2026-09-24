---
name: crossprovider codex broad-filesystem-scans-in-constrained-worktrees-
description: Broad filesystem scans in constrained worktrees should cap early
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [performance, worktree-constraints]
---

Parallelizing large `grep`/`find` operations across full repos (workspace-hub, worldenergydata) in restricted sandboxes risks timeout, context waste, and long-running process leakage. Narrow searches to specific directories/files early; kill broad scans if they don't return quickly. This is especially important when the actual deliverable is a focused summary, not an exhaustive inventory.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
