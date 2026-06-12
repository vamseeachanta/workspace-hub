---
name: crossprovider hermes wildcard-helper-imports-in-test-splits-require-e
description: Wildcard helper imports in test splits require explicit __all__ guard
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [test-structure, pytest-collection, wildcard-imports]
---

When splitting a monolithic test file and using `from helper import *`, pytest collection can silently hide missing tests if the helper module lacks `__all__`. The wildcard succeeds but may pull fewer names than intended. Solution: always define `__all__` in helper modules and audit that all prior test counts are preserved after the split; use `pytest --collect-only` to verify.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
