---
name: crossprovider codex pre-commit-hooks-warn-but-don-t-fail-in-isolated
description: Pre-commit hooks warn but don't fail in isolated worktrees
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [hooks, isolated-checkout, warning-reporting]
---

Degraded/isolated checkouts missing shared hook scripts trigger pre-commit warnings (missing external verification scripts) but do not fail the commit. Hooks complete with warnings; report the caveat in the issue comment.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
