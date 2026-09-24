---
name: crossprovider codex shared-editable-install-virtualenv-loads-stale-c
description: Shared editable-install virtualenv loads stale code from main checkout
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [environment, testing, virtualenv, python-path]
---

When a worktree's virtualenv is an editable install pointing to main, `import` statements load main's code, not the worktree's. Pytest already sets PYTHONPATH=src via config, but direct subprocess calls must explicitly set PYTHONPATH=src to exercise worktree code. Without it, baseline probes load outdated loaders and fail with null runtime errors.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
