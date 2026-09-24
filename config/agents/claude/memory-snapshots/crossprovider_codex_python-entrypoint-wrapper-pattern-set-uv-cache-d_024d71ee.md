---
name: crossprovider codex python-entrypoint-wrapper-pattern-set-uv-cache-d
description: Python entrypoint wrapper pattern: set UV_CACHE_DIR before uv run
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [python-tooling, uv, workspace-hub-patterns]
---

workspace-hub enforces `uv run --no-project python` instead of bare `python3`. Scripts that invoke Python must export `UV_CACHE_DIR` to a repo-writable path (e.g., `.claude/state/uv-cache`) before the wrapper call, or `uv` fails with Permission Denied in sandboxed environments. Mirror this in all new Python-invoking scripts and wrapper tests.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
