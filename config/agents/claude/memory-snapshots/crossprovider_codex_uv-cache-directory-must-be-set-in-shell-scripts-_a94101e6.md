---
name: crossprovider codex uv-cache-directory-must-be-set-in-shell-scripts-
description: UV cache directory must be set in shell scripts to avoid permission failures
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [uv, shell, cron, permissions, python-tooling]
---

Calling `uv run --no-project` from shell or cron contexts fails with permission errors on restricted accounts unless `UV_CACHE_DIR` is set to a repo-local writable path. This affects any background job that delegates to Python via uv.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
