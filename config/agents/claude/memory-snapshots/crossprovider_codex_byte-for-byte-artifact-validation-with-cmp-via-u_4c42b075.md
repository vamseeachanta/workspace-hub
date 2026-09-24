---
name: crossprovider codex byte-for-byte-artifact-validation-with-cmp-via-u
description: Byte-for-byte artifact validation with `cmp` via `uv run`
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [reproducibility, uv-tooling, verification]
---

To verify reproduction of generated reports, use `uv run` with a pinned `UV_CACHE_DIR` environment variable and compare output via `cmp` for exact byte-level matching. This catches silent normalization or formatting drift.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
