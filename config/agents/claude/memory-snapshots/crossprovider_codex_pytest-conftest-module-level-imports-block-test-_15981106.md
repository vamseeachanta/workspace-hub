---
name: crossprovider codex pytest-conftest-module-level-imports-block-test-
description: pytest conftest module-level imports block test discovery
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, pytest, environment, workaround]
---

The workspace-hub `tests/conftest.py` imports `plotly` at module level, which blocks entire test collection if `plotly` is missing from the environment. Workaround: run pytest with `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` to skip pytest plugin autoload and reach scoped test selection without the transitive import.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
