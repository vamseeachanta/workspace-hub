---
name: crossprovider codex worktree-audit-don-t-infer-clean-from-timed-out-
description: Worktree audit: don't infer clean from timed-out probes
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [worktree-cleanup, audit-discipline, slow-mount]
---

Use direct `.git` metadata and `/proc` evidence instead of Git status/`du` when probes timeout. Mark dirty/untracked/size as unknown; never assume clean. This prevents false-negative cleanup decisions and preserves worktrees with unverified registration.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
