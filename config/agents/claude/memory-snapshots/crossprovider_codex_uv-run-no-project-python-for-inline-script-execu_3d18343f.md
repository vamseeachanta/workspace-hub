---
name: crossprovider codex uv-run-no-project-python-for-inline-script-execu
description: uv run --no-project python for inline script execution
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [build, python, patterns, uv]
---

The repo uses `uv run --no-project python` in shell scripts to execute Python code inline (e.g., YAML parsing), not just as shebangs. This pattern isolates the Python environment per invocation without project dependencies.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
