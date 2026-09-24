---
name: crossprovider codex uv-based-scripts-need-hermetic-cache-configurati
description: uv-based scripts need hermetic cache configuration for CI/sandbox
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [shell-scripting, ci-environment, reproducibility, uv]
---

Scripts using `uv run` fail in restricted environments (CI, sandboxes) if the default user cache directory is unwritable. Export `UV_CACHE_DIR` to a repo-local path (e.g., `.cache/uv`) before any `uv run` invocation to ensure the script runs identically in sandbox, CI, and local environments.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
