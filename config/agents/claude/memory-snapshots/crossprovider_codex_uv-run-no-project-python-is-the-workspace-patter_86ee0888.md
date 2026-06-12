---
name: crossprovider codex uv-run-no-project-python-is-the-workspace-patter
description: uv run --no-project python is the workspace pattern
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [shell-python, uv-pattern, workspace-convention]
---

All Python invocations from shell scripts must use `uv run --no-project python` (not bare `python` or `python3`). This is a recurring enforcement pattern across multiple gate scripts, batch workers, and fixers. Bare invocations bypass the pinned environment.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
