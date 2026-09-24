---
name: crossprovider codex uv-cache-issue-in-sandboxed-environments
description: UV cache issue in sandboxed environments
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [tooling-quirk, uv, environment-specific]
---

`uv run` fails with read-only home cache in sandboxed/containerized environments. Workaround: set `UV_CACHE_DIR=/tmp` to use a writable temp directory for the build cache.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
