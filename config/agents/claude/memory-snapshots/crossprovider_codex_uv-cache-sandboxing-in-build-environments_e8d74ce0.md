---
name: crossprovider codex uv-cache-sandboxing-in-build-environments
description: UV cache sandboxing in build environments
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [build-tools, python-packaging, environment]
---

Build tools like `uv` fail silently when cache directories are read-only. Set `UV_CACHE_DIR=/tmp/uv-cache` to redirect cache writes to a writable location in sandboxed/containerized environments.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
