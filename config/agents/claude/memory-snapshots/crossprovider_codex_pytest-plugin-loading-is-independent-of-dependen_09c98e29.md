---
name: crossprovider codex pytest-plugin-loading-is-independent-of-dependen
description: pytest plugin loading is independent of dependency installation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [pytest, tooling-quirk, ci-integration]
---

pytest-benchmark declared in pyproject.toml and installed via `uv sync --all-extras` does not guarantee the pytest plugin loads; fixture discovery can still fail with 'fixture benchmark not found' while the plugin is absent from pytest's loaded plugins list. Verify plugin availability separately from dependency satisfaction.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
