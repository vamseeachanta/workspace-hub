---
name: crossprovider gemini pytest-ignore-collect-hook-pattern-for-test-heal
description: pytest_ignore_collect hook pattern for test health
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [pytest, conftest, refactoring]
---

Using `pytest_ignore_collect` hook in conftest.py to skip broken test paths during refactors is an effective pattern for maintaining test suite stability without deleting code. Paths not in the skip list are collected and executed.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
