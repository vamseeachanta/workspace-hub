---
name: crossprovider gemini pytest-class-scoped-fixture-scope-gotcha
description: Pytest class-scoped fixture scope gotcha
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [pytest, testing, fixture-scope, hidden-failure-mode]
---

Fixtures defined inside a test class (e.g., inside `class TestFoo:`) are class-scoped and cannot be discovered by other test modules. This manifests as 'fixture not found' during collection even if the fixture name is correct. Check fixture definition location (module vs class scope) when diagnosing fixture-not-found errors.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
