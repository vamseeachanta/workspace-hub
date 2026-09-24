---
name: crossprovider gemini class-scoped-pytest-fixtures-do-not-cross-test-c
description: Class-scoped pytest fixtures do not cross test class boundaries
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [pytest, fixtures, test-organization, test-scoping]
---

Fixtures defined within a test class with class scope are visible only to that class; adjacent classes cannot access them. When multiple test classes share a fixture during refactoring, the fixture must be promoted to module/session scope or moved to a shared conftest, otherwise tests fail with 'fixture not found' at runtime.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
