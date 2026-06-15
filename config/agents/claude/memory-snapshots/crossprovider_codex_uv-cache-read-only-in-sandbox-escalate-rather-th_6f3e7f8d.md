---
name: crossprovider codex uv-cache-read-only-in-sandbox-escalate-rather-th
description: uv cache read-only in sandbox; escalate rather than retry
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [sandbox, uv, python, testing]
---

pytest runs using `uv run` fail with '~/.cache/uv read-only' in sandboxed environments; this is a tooling constraint, not a test failure. Workaround: `UV_CACHE_DIR=/tmp/uv-cache uv run` or `.venv/bin/python`. Escalate to permissions rather than treating as flaky.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
