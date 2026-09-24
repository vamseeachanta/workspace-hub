---
name: crossprovider gemini pytest-class-scoped-fixture-scope-isolation
description: pytest class-scoped fixture scope isolation
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [pytest, fixtures, test-scoping]
---

Class-scoped fixtures defined inside one test class are not visible to sibling test classes in the same file, even if both classes inherit from the same parent. This affects fixture promotion strategy during refactors — moving a fixture up the tree or into a shared conftest may be unnecessary if only one class uses it.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
