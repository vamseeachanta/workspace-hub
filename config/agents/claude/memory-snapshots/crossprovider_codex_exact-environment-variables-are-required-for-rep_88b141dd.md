---
name: crossprovider codex exact-environment-variables-are-required-for-rep
description: Exact environment variables are required for reproducible verification workflows
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [reproducibility, sandboxing, test-isolation]
---

Sandboxed reproduction commands like 'uv run' must specify exact cache paths (UV_CACHE_DIR=/tmp/...) to ensure tests use the intended dependency set and avoid stale/fallback caches. Omitting these env vars silently uses system defaults, breaking reproducibility guarantees.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
