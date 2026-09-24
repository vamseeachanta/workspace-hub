---
name: crossprovider codex uv-cache-workaround-for-read-only-sandboxes
description: UV cache workaround for read-only sandboxes
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [tooling-quirk, sandbox, uv]
---

Build tools like uv fail to initialize cache in read-only sandboxes. Set UV_CACHE_DIR=/tmp/uv-cache to point the cache to writable temporary storage, allowing uv run, pytest, and other tools to work in constrained environments.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
