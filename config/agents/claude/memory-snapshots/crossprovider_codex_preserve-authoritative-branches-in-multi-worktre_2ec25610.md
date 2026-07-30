---
name: crossprovider codex preserve-authoritative-branches-in-multi-worktre
description: Preserve authoritative branches in multi-worktree scenarios via ancestry lineage
metadata:
  type: reference
  source: codex
  bridged: 2026-07-16
  tags: [workflow, worktrees, multi-session]
---

When auditing existing work with multiple worktrees for the same issue, determine authoritative branches via commit ancestry (e.g., `feature/issue-166-evidence-ledger-loop` ancestral to `feature/issue-166-evidence-ledger-run` = run is authoritative). Mark divergent dead-ends and do not edit parallel sessions' worktrees.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
