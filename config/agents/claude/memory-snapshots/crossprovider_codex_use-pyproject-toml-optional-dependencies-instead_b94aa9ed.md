---
name: crossprovider codex use-pyproject-toml-optional-dependencies-instead
description: Use pyproject.toml optional-dependencies instead of inline --with flags
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [tooling, dependency-management, uv]
---

Define `[project.optional-dependencies.workqueue]` in `pyproject.toml` and invoke via `uv run --extra workqueue` instead of `--with markdown --with PyYAML --with bleach`. Cleaner, version-tracked, reusable across invocations.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
