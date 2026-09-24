---
name: crossprovider gemini pythonpath-based-cross-repo-testing-is-anti-patt
description: PYTHONPATH-based cross-repo testing is anti-pattern
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [python, testing, dependencies]
---

Manual PYTHONPATH manipulation for cross-repo test execution fails when downstream repos have unresolved third-party dependencies. Modern Python projects (uv, pyproject.toml) should use package-manager-backed resolution (`uv run -e <path>`) or isolated venvs, not PYTHONPATH injection.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
