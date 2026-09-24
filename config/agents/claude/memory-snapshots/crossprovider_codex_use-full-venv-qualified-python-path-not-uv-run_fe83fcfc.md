---
name: crossprovider codex use-full-venv-qualified-python-path-not-uv-run
description: Use full venv-qualified Python path, not uv run
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [tooling, venv, python]
---

Always specify full path (`/path/to/.venv/bin/python`) when working with repo-specific virtual environments, not `uv run`. Pinned dependencies and console-script resolution depend on the exact interpreter.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
