---
name: crossprovider gemini patch-dict-sys-modules-for-optional-import-testi
description: Patch.dict(sys.modules) for optional import testing
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [testing, mocking, dependencies]
---

When testing behavior with missing optional dependencies, use `patch.dict(sys.modules, {"package": None})` instead of mocking `__import__` directly. Simpler, more readable, and correctly triggers ImportError on actual import attempts.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
