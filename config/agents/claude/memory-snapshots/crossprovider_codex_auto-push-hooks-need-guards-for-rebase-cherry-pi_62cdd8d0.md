---
name: crossprovider codex auto-push-hooks-need-guards-for-rebase-cherry-pi
description: Auto-push hooks need guards for rebase/cherry-pick/amend, explicit upstream resolution, and trunk branching
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-workflow, auto-push, correctness]
---

Post-commit auto-push must suppress pushes during history rewrites (rebase, cherry-pick, amend, merge-conflict recovery) to avoid publishing intermediate commits. Always push to the configured upstream (`@{u}`) resolved at guard-check time, not hard-coded `origin`. Feature branches created for work must branch from trunk explicitly (e.g., `git checkout -b feature/X main`), not from current HEAD, which can inherit unrelated commits.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
