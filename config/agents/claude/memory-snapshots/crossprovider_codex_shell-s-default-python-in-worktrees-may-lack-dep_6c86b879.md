---
name: crossprovider codex shell-s-default-python-in-worktrees-may-lack-dep
description: Shell's default Python in worktrees may lack dependencies — use .venv/bin
metadata:
  type: reference
  source: codex
  bridged: 2026-08-04
  tags: [environment-setup, worktrees, dependencies, python]
---

The shell's default `python` in a worktree checkout can be misconfigured or lack required dependencies (e.g., SciPy). Always prepend worktree-local `.venv/bin/python` for reproducibility and accurate error reporting.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
