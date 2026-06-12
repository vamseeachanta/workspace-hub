---
name: crossprovider codex pytest-class-scoped-fixtures-don-t-cross-sibling
description: Pytest class-scoped fixtures don't cross sibling class boundaries
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [pytest, fixtures, testing, gotcha]
---

In a single test module, a class-scoped fixture defined in one test class is not visible to sibling test classes even if they appear in the same file. Use module-scoped or function-scoped fixtures if multiple test classes need access, or promote to conftest.py.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
