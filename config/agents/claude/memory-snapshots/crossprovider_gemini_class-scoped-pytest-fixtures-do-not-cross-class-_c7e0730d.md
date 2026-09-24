---
name: crossprovider gemini class-scoped-pytest-fixtures-do-not-cross-class-
description: Class-scoped pytest fixtures do not cross class boundaries
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [pytest, test-fixtures, test-design]
---

When multiple test classes need the same fixture, class-scoped fixtures defined within one class are not visible to other classes. Shared fixtures must be defined at module or conftest level. This creates a pattern where test collections succeed but execution fails with fixture-not-found errors when crossing class boundaries.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
