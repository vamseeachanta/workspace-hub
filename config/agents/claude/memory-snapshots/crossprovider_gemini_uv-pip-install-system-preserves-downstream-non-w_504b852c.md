---
name: crossprovider gemini uv-pip-install-system-preserves-downstream-non-w
description: uv pip install --system preserves downstream non-wrapped execution
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [uv, python, ci]
---

Use `uv pip install --system` when downstream (pytest/mypy) runs without `uv run` prefix; `uv sync --frozen` breaks bare runners.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
