---
name: crossprovider gemini mypy-isolation-via-uv-tool-run-loses-project-dep
description: Mypy isolation via uv tool run loses project dependencies
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [python, type-checking, tool-isolation, performance]
---

WRK-1056: Running `uv tool run mypy` in isolated environment can't resolve project's installed dependencies, degrading to `Any` for third-party types. Use `uv run mypy` (within repo's environment) instead, or accept reduced type-checking effectiveness.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
