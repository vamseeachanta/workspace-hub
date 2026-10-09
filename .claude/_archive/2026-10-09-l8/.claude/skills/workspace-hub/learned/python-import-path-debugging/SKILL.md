---
name: python-import-path-debugging
description: Diagnose ModuleNotFoundError when a package is installed but still fails to import
version: 1.0.0
source: auto-extracted
extracted: 2026-04-10
metadata:
  tags: ["python", "debugging", "environment", "imports"]
---

# Python Import Path Debugging

When a ModuleNotFoundError occurs despite the package being installed, the issue is typically a Python path/environment mismatch. Check: (1) which Python executable the CLI script uses (check shebang and `which`), (2) which environment has the package installed vs. which the script is executing in, (3) whether the script is using a virtual environment that differs from your active shell environment. Verify with `python -c "import module; print(module.__file__)"` to confirm the correct interpreter is being used.