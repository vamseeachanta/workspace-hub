---
name: crossprovider codex read-only-review-bytecode-and-cache-cleanup
description: Read-only review bytecode and cache cleanup
metadata:
  type: reference
  source: codex
  bridged: 2026-07-01
  tags: [tooling, testing, python]
---

`PYTHONDONTWRITEBYTECODE=1` does not prevent import-time __pycache__ generation; use `UV_CACHE_DIR=.claude/state/uv-cache` override or manual cleanup for truly read-only reviews.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
