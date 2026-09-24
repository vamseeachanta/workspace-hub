---
name: crossprovider codex pythondontwritebytecode-does-not-guarantee-no-ca
description: PYTHONDONTWRITEBYTECODE does not guarantee no cache generation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [python, cache, cleanup]
---

Even with `PYTHONDONTWRITEBYTECODE=1`, importing and executing Python code can generate `__pycache__/` in shared directories if the runtime falls back to bytecode caching. Verification/test runs in shared repos need explicit removal of generated cache directories before cleanup audit.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
