---
name: crossprovider codex pytest-conftest-pytest-sessionfinish-hook-blocks
description: pytest conftest pytest_sessionfinish hook blocks collection
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [pytest, performance, antipattern, conftest]
---

Expensive work (database queries, analysis) at pytest_sessionfinish hangs collection indefinitely. Diagnosis: timeout pytest --collect-only; capture stack via faulthandler to find conftest line. Fix: move work outside collection hooks or use optional/lazy fixtures.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
