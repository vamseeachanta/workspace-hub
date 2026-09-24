---
name: crossprovider codex test-quarantine-removal-requires-pytest-config-s
description: Test quarantine removal requires pytest config sync
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, pytest, configuration]
---

When removing collection skips from conftest.py, also check and remove matching ignore patterns from pytest config (e.g., `pyproject.toml --ignore=...`). Tests can remain hidden by duplicate quarantine mechanisms even after removing one layer.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
