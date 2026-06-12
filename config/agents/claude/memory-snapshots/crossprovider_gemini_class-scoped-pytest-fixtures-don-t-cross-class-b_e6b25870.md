---
name: crossprovider gemini class-scoped-pytest-fixtures-don-t-cross-class-b
description: Class-scoped pytest fixtures don't cross class boundaries in same file
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [pytest, fixtures, refactoring, test-organization]
---

Pytest fixtures with class scope are visible only within the class they're defined in; sibling classes in the same file cannot access them. During refactoring that splits legacy and modern code into separate test classes, class-scoped fixtures become invisible to legacy classes, causing test failures that weren't caught in earlier unified structures.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
