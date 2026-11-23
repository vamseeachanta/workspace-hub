---
name: diagnose-venv-shebang-import-errors
description: Debugging pattern for ModuleNotFoundError when CLI entry points use wrong Python interpreter
version: 1.0.0
source: auto-extracted
extracted: 2026-04-10
metadata:
  tags: ["python", "venv", "debugging", "import-errors", "cli"]
---

# Diagnose Virtual Environment Shebang Import Errors

When a CLI tool fails with ModuleNotFoundError despite the package being installed, check if the entry point shebang (`#!/usr/bin/env python3`) resolves to the system Python instead of the venv Python. Verify by: (1) checking which python the shebang resolves to, (2) confirming the package exists in the venv but not system python, (3) updating the shebang to point directly to the venv's Python binary (e.g., `~/.venv/bin/python3`). If the shebang keeps reverting after updates, investigate post-install hooks that may regenerate entry points with generic shebangs.