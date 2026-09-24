---
name: crossprovider codex local-git-tracking-refs-diverge-from-live-remote
description: Local git tracking refs diverge from live remote without local status warning
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-ls-remote, upstream-tracking, ecosystem-audit]
---

A repo can report clean local status (no ahead/behind vs local upstream ref) while local `origin/main` ref is stale vs live remote (verified via `git ls-remote`). Ecosystem audits must use `git ls-remote` to catch these silent divergences; local refs alone are incomplete.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
