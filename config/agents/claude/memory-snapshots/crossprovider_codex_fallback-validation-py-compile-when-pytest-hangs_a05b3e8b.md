---
name: crossprovider codex fallback-validation-py-compile-when-pytest-hangs
description: Fallback validation: py_compile when pytest hangs
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [pytest-timeout, fallback-validation, uv-isolation]
---

When `uv run pytest` hangs indefinitely during environment setup, switch to `py_compile` (syntax-only, no test execution) or `--no-project python -m py_compile` to verify code is at least parseable without triggering full project initialization.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
