---
name: crossprovider codex pytest-collection-overhead-diagnosis-with-pytest
description: Pytest collection overhead diagnosis with PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [pytest, testing, performance-diagnosis]
---

When pytest hangs during collection phase (before tests run), disable plugin autoload with `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` to separate plugin loading overhead from actual test failures. Helps determine whether hang is due to slow plugin initialization or broken test code.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
