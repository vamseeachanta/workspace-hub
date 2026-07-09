---
name: crossprovider codex pytest-conftest-module-imports-block-full-suite-
description: Pytest conftest module imports block full suite; use venv or direct smoke tests
metadata:
  type: reference
  source: codex
  bridged: 2026-07-07
  tags: [test-infrastructure, pytest-config, environment-setup]
---

When repo conftest.py imports modules not installed in system Python (e.g., plotly), pytest hangs before test collection and never returns. Workaround: use the repo's `.venv` and run pytest directly through it, or call test files with `venv/bin/python -m pytest`, bypassing system conftest. Direct import/smoke tests still work for basic behavioral verification even if the full suite is blocked.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
