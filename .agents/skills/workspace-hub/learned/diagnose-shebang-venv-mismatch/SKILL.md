---
name: diagnose-shebang-venv-mismatch
description: Identify and fix shebang mismatches when CLI tools resolve to system Python instead of their virtual environment
version: 1.0.0
source: auto-extracted
extracted: 2026-04-10
metadata:
  tags: ["python", "venv", "debugging", "cli-tools", "shebang"]
---

# Diagnose Shebang vs Venv Mismatch

When a CLI tool fails with ModuleNotFoundError for packages that are installed in its venv, the entry point shebang may be pointing to system Python instead of the venv's Python. Check the shebang in `/usr/local/bin/<tool>` or `~/.local/bin/<tool>` — it should reference the venv's Python (`/path/to/venv/bin/python3`), not `/usr/bin/env python3`. Update the shebang directly or check if the tool's update process regenerates it with a generic shebang, requiring a permanent fix strategy.