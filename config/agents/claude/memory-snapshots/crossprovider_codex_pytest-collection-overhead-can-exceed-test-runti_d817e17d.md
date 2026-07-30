---
name: crossprovider codex pytest-collection-overhead-can-exceed-test-runti
description: Pytest collection overhead can exceed test runtime on large repos
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [testing, performance, tools]
---

Direct targeted function invocation (pytest tests/test_foo.py::test_bar) bypasses collection overhead. On large repos, collection alone can take minutes while actual test execution is seconds.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
