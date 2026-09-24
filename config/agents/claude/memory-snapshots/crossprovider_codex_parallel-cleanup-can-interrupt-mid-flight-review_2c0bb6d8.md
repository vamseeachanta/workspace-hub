---
name: crossprovider codex parallel-cleanup-can-interrupt-mid-flight-review
description: Parallel cleanup can interrupt mid-flight reviews
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [process-safety, cleanup-race, worktree-hazard]
---

External deletion of `/tmp/wt-*` or `/tmp/vision-*` paths during active verification breaks ongoing commands and leaves reviews incomplete. Reviews should validate early and fail-closed; use GitHub patch fetch (`gh pr diff`) as fallback when worktrees are unavailable.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
