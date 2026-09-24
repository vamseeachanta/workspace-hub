---
name: crossprovider codex cleanup-audit-gate-pattern-before-review-sign-of
description: Cleanup audit gate pattern before review sign-off
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [review-process, governance, cleanup, quality-gate]
---

Before finalizing a review, run a read-only cleanup audit covering: worktree status/stashes, scratch files, cleanup locks, and session handoff state. This gate prevents signing off with unexpected residue that later sessions must clean up.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
