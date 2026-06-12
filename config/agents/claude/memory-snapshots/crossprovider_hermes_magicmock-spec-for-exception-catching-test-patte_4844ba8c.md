---
name: crossprovider hermes magicmock-spec-for-exception-catching-test-patte
description: MagicMock spec=[] for exception-catching test patterns
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, mocking, pytest, python]
---

Testing code with try/except around `getattr()` requires `MagicMock(spec=[])` to force AttributeError on undefined attributes. Bare `MagicMock()` returns another MagicMock (truthy) instead of raising, breaking the exception handler. Essential for testing defensive code that catches and handles missing attributes.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
