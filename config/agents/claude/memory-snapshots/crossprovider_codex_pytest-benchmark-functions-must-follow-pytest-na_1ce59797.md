---
name: crossprovider codex pytest-benchmark-functions-must-follow-pytest-na
description: pytest-benchmark functions must follow pytest naming conventions (test_*)
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [pytest-discovery, naming-conventions, test-framework]
---

Benchmark functions named `bench_*` are silently skipped by pytest discovery, even inside `test_*.py` files. Pytest collects only `test_*` by default. Rename to `test_bench_*` or use explicit `pytest_plugins` configuration if needed.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
