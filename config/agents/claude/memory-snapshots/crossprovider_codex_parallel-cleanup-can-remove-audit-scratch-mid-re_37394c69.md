---
name: crossprovider codex parallel-cleanup-can-remove-audit-scratch-mid-re
description: Parallel cleanup can remove audit scratch mid-review; use ref-based fallbacks
metadata:
  type: reference
  source: codex
  bridged: 2026-06-15
  tags: [parallel-work, audit-resilience, git-refs]
---

Long-running audits may have their scratch directories removed by parallel cleanup processes (e.g., `git worktree remove /tmp/wt-vbatch-165` mid-review). Evidence captured before removal remains valid via committed refs. Use `git diff origin/base...head` and `gh pr diff` to verify changed files without relying on worktree paths; ref-based checks are resilient to mid-review cleanup.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
