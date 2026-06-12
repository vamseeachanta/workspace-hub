---
name: crossprovider gemini python-3-8-type-hints-require-from-future-import
description: Python 3.8 type hints require `from __future__ import annotations`
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [python, typing, compatibility]
---

When using modern syntax like `dict[str, Any]` in Python 3.8, must add `from __future__ import annotations` to the file. Without it, code raises `TypeError` at runtime. This applies to all files using parameterized generics, not just type-stub files (WRK-1079).

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
