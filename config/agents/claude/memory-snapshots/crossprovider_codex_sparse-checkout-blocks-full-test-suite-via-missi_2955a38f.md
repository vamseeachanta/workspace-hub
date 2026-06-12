---
name: crossprovider codex sparse-checkout-blocks-full-test-suite-via-missi
description: Sparse checkout blocks full test suite via missing imports
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [sparse-checkout, pytest, uv-isolation]
---

Sparse checkouts missing `workspace_hub`, `src`, `digitalmodel` Python modules prevent `uv run pytest` from collecting tests (hangs indefinitely or timeouts after 30-90s). Workaround: use `uv run --no-project` with explicit deps, run targeted test paths directly, or fall back to `py_compile` for syntax-only validation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
