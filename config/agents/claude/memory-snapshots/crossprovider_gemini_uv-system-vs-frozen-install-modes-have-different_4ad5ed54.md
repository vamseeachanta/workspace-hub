---
name: crossprovider gemini uv-system-vs-frozen-install-modes-have-different
description: uv --system vs --frozen install modes have different downstream effects
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [ci, uv, python, package-management]
---

`uv sync --frozen` creates a sandboxed environment; downstream commands (pytest, mypy, flake8) that run WITHOUT `uv run` prefix will fail. Use `uv pip install --system` to preserve non-sandboxed path for downstream tools. This matters when existing CI workflows depend on tools being available globally.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
