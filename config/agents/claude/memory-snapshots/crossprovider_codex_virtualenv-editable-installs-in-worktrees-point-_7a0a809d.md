---
name: crossprovider codex virtualenv-editable-installs-in-worktrees-point-
description: Virtualenv editable installs in worktrees point to stale checkouts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [python, environment, worktree]
---

When the shared venv's editable install points to an older checkout, direct Python probes load the old code. Set `PYTHONPATH=src` for worktree-scoped tests; pytest config handles it, but manual validation must be explicit.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
