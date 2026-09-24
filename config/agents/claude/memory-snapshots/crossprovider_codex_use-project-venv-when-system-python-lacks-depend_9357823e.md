---
name: crossprovider codex use-project-venv-when-system-python-lacks-depend
description: Use project venv when system Python lacks dependencies
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [environment, python, dependency-management, testing]
---

When shell `python` lacks required packages (e.g., SciPy), prepend `.venv/bin/` to all `python -m` commands rather than inventing workarounds or assuming unavailability.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
