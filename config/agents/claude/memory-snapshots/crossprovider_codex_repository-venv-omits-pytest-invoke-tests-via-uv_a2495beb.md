---
name: crossprovider codex repository-venv-omits-pytest-invoke-tests-via-uv
description: Repository .venv omits pytest; invoke tests via uv
metadata:
  type: reference
  source: codex
  bridged: 2026-08-15
  tags: [pytest, uv, test-environment, repo-constraint]
---

Test invocation requires uv run --with-editable '.[test]' python -m pytest. The .venv is intentionally minimal; pytest is bootstrapped on-demand for test isolation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
