---
name: crossprovider gemini pytest-hook-override-precedence-over-config-file
description: pytest hook override precedence over config files
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [pytest, configuration, testing]
---

pytest.ini and pyproject.toml declarations are overridden by conftest.py hooks (e.g., pytest_ignore_collect returning False). Partial skip lists in conftest won't solve collection errors if they don't cover all failing files—collection still fails on uncovered errors, blocking CI even if some are skipped.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
