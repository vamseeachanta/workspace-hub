---
name: crossprovider codex uv-cache-dir-required-for-uv-run-in-restricted-c
description: UV_CACHE_DIR required for uv run in restricted cron environments
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [python-tooling, nightly-cron, environment-isolation]
---

Nightly cron jobs using `uv run --no-project python` fail with 'Permission denied' on /home/.cache/uv unless UV_CACHE_DIR is explicitly set to a writable repo-local or temp path. The issue appears in both shell entrypoints and Python subprocesses that shell out to uv.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
