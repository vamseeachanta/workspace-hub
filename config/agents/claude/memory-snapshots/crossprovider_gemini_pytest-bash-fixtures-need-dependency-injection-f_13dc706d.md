---
name: crossprovider gemini pytest-bash-fixtures-need-dependency-injection-f
description: Pytest bash fixtures need dependency injection for path mocking
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [pytest, dependency-injection, bash-testing]
---

Bash scripts with hardcoded paths (e.g., `source /opt/openfoam2312/bashrc`) cannot be cleanly mocked in Pytest fixtures without dependency injection. Export path lists via environment variables (e.g., `OPENFOAM_BASHRC_PATHS`) so tests can override/stub.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
