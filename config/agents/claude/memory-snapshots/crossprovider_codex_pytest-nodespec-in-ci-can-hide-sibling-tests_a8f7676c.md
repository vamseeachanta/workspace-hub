---
name: crossprovider codex pytest-nodespec-in-ci-can-hide-sibling-tests
description: pytest nodespec in CI can hide sibling tests
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [pytest, ci, testing]
---

Specifying `file.py::test_name` in a CI workflow may prevent pytest from discovering other tests in the same file. Switching to full-file paths ensures complete test suite execution and prevents regressions where changes to untested sibling functions slip through.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
