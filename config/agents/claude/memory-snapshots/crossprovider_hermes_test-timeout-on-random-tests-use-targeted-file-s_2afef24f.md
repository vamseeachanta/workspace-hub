---
name: crossprovider hermes test-timeout-on-random-tests-use-targeted-file-s
description: Test timeout on random tests; use targeted file scoping and uv run for clean imports
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, performance, imports, uv]
---

Long-running test suites with randomization timeout under heavy load. Use `uv run pytest -q <specific_test_file>` to isolate files and reduce scope. Import paths via `import pytest` may hang >30s on venv; rely on CI or verify syntax via `py_compile` instead of pytest.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
