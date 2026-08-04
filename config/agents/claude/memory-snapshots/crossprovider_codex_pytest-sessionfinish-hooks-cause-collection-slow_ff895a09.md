---
name: crossprovider codex pytest-sessionfinish-hooks-cause-collection-slow
description: pytest sessionfinish hooks cause collection slowness, not just imports
metadata:
  type: reference
  source: codex
  bridged: 2026-08-03
  tags: [pytest, diagnostics, testing]
---

Collection can appear to hang or be extremely slow when `conftest.py` hooks like `pytest_sessionfinish` do real work post-collection—database queries, file I/O, regressions analysis. Disabling plugins/conftest won't help if the actual cost is in hooks. Identify via faulthandler stack dumps at 30/60/90s intervals to find the exact hook and file:line.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
