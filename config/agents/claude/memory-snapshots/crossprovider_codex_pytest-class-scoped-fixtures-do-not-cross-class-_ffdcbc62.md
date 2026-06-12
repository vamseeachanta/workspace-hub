---
name: crossprovider codex pytest-class-scoped-fixtures-do-not-cross-class-
description: pytest class-scoped fixtures do not cross class boundaries
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [pytest, fixtures, scope, testing]
---

A fixture defined inside one test class with class scope is invisible to sibling test classes in the same module, even if they need it. Cross-class fixture access requires module or conftest scope, but promotion is only mandatory if all classes actually consume it.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
