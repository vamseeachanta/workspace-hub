---
name: crossprovider codex uv-cache-read-only-in-sandbox-environment
description: UV cache read-only in sandbox environment
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [tooling-quirk, python-uv, sandbox]
---

When ~/.cache/uv is read-only in sandbox, use `UV_CACHE_DIR=/tmp/uv-cache uv run` or fall back to `.venv/bin/python`. Concurrent `uv run` attempts fail on environment setup; run tests sequentially or use pre-built venv instead of parallel environment creation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
