---
name: crossprovider codex shared-state-mutations-git-worktree-cleanup-bran
description: Shared-state mutations (git worktree cleanup, branch ops) are audit red flags
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [git, cron-design, safety]
---

Scripts performing repo ecosystem cleanup (worktree prune, local branch deletion, stale lock removal, push/merge cycles) are high-risk for read-only audits even if marked `--dry-run`. Prefer building an independent, read-only audit that does NOT rely on reusing mutation scripts; verify each probe independently.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
