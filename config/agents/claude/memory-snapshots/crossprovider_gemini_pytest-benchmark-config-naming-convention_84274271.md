---
name: crossprovider gemini pytest-benchmark-config-naming-convention
description: Pytest benchmark config naming convention
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [pytest, config, gotcha]
---

In pyproject.toml, the pytest-benchmark plugin config section must be named `[tool.pytest-benchmark]` (with hyphen), not `[tool.pytest.benchmark]` (with dot). The dot form causes pyproject.toml parsing conflicts; the hyphen form is the correct TOML key.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
