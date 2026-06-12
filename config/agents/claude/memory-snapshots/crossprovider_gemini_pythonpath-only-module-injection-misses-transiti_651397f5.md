---
name: crossprovider gemini pythonpath-only-module-injection-misses-transiti
description: PYTHONPATH-only module injection misses transitive deps
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [python, dependency-management, cross-repo-testing]
---

Manual `PYTHONPATH=<repo>/src` injection finds the code but not third-party dependencies. Transitive imports fail with ModuleNotFoundError, masking API contract breaks. Use `uv run --with <package>` or `uv pip install -e <path>` to activate full environment.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
