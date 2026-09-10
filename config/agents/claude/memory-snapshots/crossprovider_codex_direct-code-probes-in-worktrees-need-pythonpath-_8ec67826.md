---
name: crossprovider codex direct-code-probes-in-worktrees-need-pythonpath-
description: Direct code probes in worktrees need PYTHONPATH=src when shared venv points to main
metadata:
  type: reference
  source: codex
  bridged: 2026-07-30
  tags: [worktree, editable-install, environment]
---

When a shared venv's editable install points to main checkout, direct Python probes load from main unless PYTHONPATH=src redirects them. pytest uses repo configuration automatically, but scripts and interactive probes need explicit PYTHONPATH.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
