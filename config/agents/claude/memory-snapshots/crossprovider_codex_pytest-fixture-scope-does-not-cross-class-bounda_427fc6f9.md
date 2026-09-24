---
name: crossprovider codex pytest-fixture-scope-does-not-cross-class-bounda
description: Pytest fixture scope does not cross class boundaries
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [pytest, test-fixtures]
---

Class-scoped fixtures defined inside a test class (e.g., `@pytest.fixture(scope='class')` or method fixtures in a class body) are invisible to methods in other test classes, even within the same file. This is a pytest scoping rule, not an issue with the fixture definition.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
