---
name: crossprovider gemini uv-cache-must-be-explicitly-exported-in-sandbox-
description: UV cache must be explicitly exported in sandbox/CI
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [uv, sandbox, ci, hermiticity]
---

Export `UV_CACHE_DIR` before invoking uv in sandbox or CI scripts to prevent cache pollution across isolated contexts. This is essential for hermetic builds.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
