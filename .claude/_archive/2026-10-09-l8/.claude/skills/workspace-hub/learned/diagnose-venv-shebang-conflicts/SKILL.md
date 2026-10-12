---
name: diagnose-venv-shebang-conflicts
description: Debugging pattern for resolving ModuleNotFoundError when CLI entry points use wrong Python interpreter
version: 1.0.0
source: auto-extracted
extracted: 2026-04-10
metadata:
  tags: ["python", "virtualenv", "debugging", "cli"]
---

# Diagnose Virtual Environment Shebang Conflicts

When a CLI tool installed via pip fails with ModuleNotFoundError despite packages being installed, check if the entry point shebang points outside the venv. Compare the shebang in `~/.local/bin/<tool>` against the venv's actual python path (`<venv>/bin/python3`). If they differ, the generic `#!/usr/bin/env python3` may resolve to system python lacking venv packages. Update the shebang to point directly to the venv's python, or investigate if package updates are regenerating entry points with incorrect shebangs.