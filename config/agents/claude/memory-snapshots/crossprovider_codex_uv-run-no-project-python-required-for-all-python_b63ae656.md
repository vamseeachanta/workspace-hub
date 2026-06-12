---
name: crossprovider codex uv-run-no-project-python-required-for-all-python
description: uv run --no-project python required for all Python CLI execution
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [environment, policy]
---

Workspace policy (per context.md): all Python scripts/configs must use `uv run --no-project python -c` not bare `python3`. Ensures consistent Python runtime per repo-level environment rules.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
