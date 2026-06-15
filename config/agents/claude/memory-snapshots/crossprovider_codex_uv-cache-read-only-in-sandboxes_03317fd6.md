---
name: crossprovider codex uv-cache-read-only-in-sandboxes
description: UV cache read-only in sandboxes
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [uv, sandbox, environment, tooling]
---

Default `~/.cache/uv` is read-only in bwrap sandboxes. Workaround: `UV_CACHE_DIR=/tmp/uv-cache uv run ...` to write cache to writable temp directory.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
