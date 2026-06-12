---
name: crossprovider hermes pytest-raises-is-idiomatic-for-exception-testing
description: pytest.raises() is idiomatic for exception testing
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, pytest, python]
---

Prefer `pytest.raises(...)` context manager over manual try/except blocks in test code. Gemini review feedback validated this pattern; it's cleaner and more idiomatic than explicit exception handling in tests.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
