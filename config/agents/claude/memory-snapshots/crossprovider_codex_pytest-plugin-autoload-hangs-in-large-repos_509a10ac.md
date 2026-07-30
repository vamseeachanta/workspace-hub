---
name: crossprovider codex pytest-plugin-autoload-hangs-in-large-repos
description: pytest plugin autoload hangs in large repos
metadata:
  type: reference
  source: codex
  bridged: 2026-07-08
  tags: [pytest, testing, debugging, large-repos]
---

Use `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` with cleared `PYTEST_ADDOPTS` when pytest hangs before test collection. Plugins like faker/hypothesis auto-discover and block collection; disabling them allows tests to run.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
