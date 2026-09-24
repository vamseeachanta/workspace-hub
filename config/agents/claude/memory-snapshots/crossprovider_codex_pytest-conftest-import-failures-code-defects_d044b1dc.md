---
name: crossprovider codex pytest-conftest-import-failures-code-defects
description: Pytest conftest import failures != code defects
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, pytest, debugging]
---

When conftest.py imports fail, pytest cannot collect tests. This is a test-harness issue, not evidence the diff is wrong. Distinguish test infrastructure failures from code defects when reviewing test-run output.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
