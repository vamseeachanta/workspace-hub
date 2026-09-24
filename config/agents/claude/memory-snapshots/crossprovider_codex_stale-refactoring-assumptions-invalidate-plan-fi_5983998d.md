---
name: crossprovider codex stale-refactoring-assumptions-invalidate-plan-fi
description: Stale refactoring assumptions invalidate plan files against live HEAD; verify implementation state
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, stale-state, codex-pattern]
---

When reviewing a plan against the repo, check if proposed files/functions have been recently refactored. #3139 claimed `_skill_identity.py` was missing but it already existed at HEAD. Always verify current implementation state and line numbers; do not trust a plan's "missing/new" claims without checking live code.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
