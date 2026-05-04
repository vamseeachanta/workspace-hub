---
name: diagnose-shebang-virtualenv-import-errors
description: Debugging pattern for ModuleNotFoundError when CLI entry points use wrong Python interpreter
version: 1.0.0
source: auto-extracted
extracted: 2026-04-10
metadata:
  tags: ["python", "virtualenv", "debugging", "cli", "import-errors"]
---

# Diagnose Shebang vs Virtual Environment Import Errors

When a CLI tool installed in a venv throws ModuleNotFoundError for packages that exist in that venv, check if the entry point shebang uses the system Python instead of the venv Python. Verify the actual shebang in ~/.local/bin/<tool>, check which python it resolves to with `which python3`, and compare against the venv's bin/python3 path. If mismatched, update the shebang to point directly to the venv interpreter. Note: this can revert on tool updates if the installer regenerates the entry point.