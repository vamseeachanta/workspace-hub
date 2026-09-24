---
name: crossprovider codex pytest-collect-only-executes-sessionfinish-hooks
description: pytest --collect-only executes sessionfinish hooks; causes hidden latency in CI gates
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [pytest, collection, conftest, ci-gates, performance]
---

Collect-only normally means "don't run tests", but pytest still fires conftest hooks like `pytest_sessionfinish`. If those hooks do real work (SQLite queries, regression analysis, etc.), collection appears to hang when it is actually in post-collection hooks. Observed in worldenergydata where regression detection queries a 59 MiB database for each of 14.4k statistics rows; real collection is ~1-3 seconds, sessionfinish adds 100+ seconds. Critical for diagnosing <30s CI collection budgets.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
