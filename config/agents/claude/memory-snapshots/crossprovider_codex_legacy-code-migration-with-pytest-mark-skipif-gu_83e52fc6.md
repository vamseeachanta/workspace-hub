---
name: crossprovider codex legacy-code-migration-with-pytest-mark-skipif-gu
description: Legacy code migration with pytest.mark.skipif guards
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [refactoring, architectural-pattern, test-strategy]
---

When APIs are refactored/removed, decorate legacy-dependent tests with @pytest.mark.skipif(availability_check) to skip gracefully instead of failing collection. Enables gradual migration without breaking the test suite during transitions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
