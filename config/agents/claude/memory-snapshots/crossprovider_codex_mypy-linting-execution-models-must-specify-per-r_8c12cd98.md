---
name: crossprovider codex mypy-linting-execution-models-must-specify-per-r
description: Mypy/linting execution models must specify per-repo context—not assume centralized workspace invocation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [linting, dependency-management, execution-model]
---

Centralizing a command like `uv run mypy <repo>/src` from workspace root is under-specified: it may not use the repo's dependencies, config, or Python environment. Instead specify whether to `cd` into each repo, which invocation mode to use (repo-local vs tool-run), and what fallback applies when the tool is missing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
