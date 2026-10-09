---
name: diagnose-venv-shebang-mismatch
description: Diagnose and fix ModuleNotFoundError caused by entry point shebang pointing outside virtual environment
version: 1.0.0
source: auto-extracted
extracted: 2026-04-10
metadata:
  tags: ["python", "venv", "debugging", "shebangs"]
---

# Diagnose Virtual Environment Shebang Mismatch

When a CLI tool throws ModuleNotFoundError for an installed package, check if the entry point shebang (`#!/usr/bin/env python3`) resolves to a different Python than the venv where the package is installed. Verify the installed script location (`which <command>`) against the actual venv path. Update the shebang to explicitly point to the venv's Python binary (`#!/path/to/venv/bin/python3`). Note: reinstalls/updates may revert shebangs to generic defaults — check post-install hooks if this recurs.