---
name: diagnose-shebang-venv-import-errors
description: Troubleshoot ModuleNotFoundError in CLI tools by identifying shebang-venv mismatches
version: 1.0.0
source: auto-extracted
extracted: 2026-04-10
metadata:
  tags: ["python", "venv", "debugging", "cli-tools"]
---

# Diagnose Shebang vs Virtual Environment Import Errors

When a CLI tool fails with ModuleNotFoundError despite the package being installed, check if the shebang in `/usr/local/bin/` or `~/.local/bin/` points to system Python instead of the venv Python. Verify the actual Python interpreter being used by examining the shebang (`#!/usr/bin/env python3` vs `/path/to/venv/bin/python3`). If mismatched, update the shebang to explicitly point to the venv's Python executable. Be aware that auto-update mechanisms may revert custom shebangs—check for post-install scripts that regenerate entry points.