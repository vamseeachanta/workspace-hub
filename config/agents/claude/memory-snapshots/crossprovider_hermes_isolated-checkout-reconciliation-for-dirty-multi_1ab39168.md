---
name: crossprovider hermes isolated-checkout-reconciliation-for-dirty-multi
description: Isolated-checkout reconciliation for dirty multi-session repos
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-workflow, worktree, multi-session, dirty-state]
---

When primary repo has accumulated dirt and multiple active workers (Hermes/Claude sessions), use separate worktree to safely commit/push changes without disturbing live cwd. Primary rebases when idle via `git fetch && git rebase origin/main`. Avoids lock races, git status storms, and cwd-disturbance errors.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
