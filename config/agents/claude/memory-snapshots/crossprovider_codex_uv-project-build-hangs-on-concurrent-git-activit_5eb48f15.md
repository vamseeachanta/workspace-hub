---
name: crossprovider codex uv-project-build-hangs-on-concurrent-git-activit
description: uv project build hangs on concurrent Git activity; use --no-project isolation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [uv, python, build, worktree, performance]
---

`uv run pytest` rebuilds `.venv` and hangs during package setup when Git is saturated by parallel lanes. Switch to `uv run --no-project --with pytest` to validate isolated modules/tests; normal project-synced path remains blocked but pure-Python validation succeeds.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
