---
name: crossprovider gemini pyproject-toml-tool-pytest-benchmark-naming-conf
description: pyproject.toml [tool.pytest.benchmark] naming conflict requires [tool.pytest-benchmark]
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [python-config, pytest, quirk]
---

Pydantic/pytest-benchmark interaction: [tool.pytest.benchmark] conflicts with Pydantic's [tool.pytest] config section. Rename to [tool.pytest-benchmark] to avoid parser ambiguity. This was discovered during WRK-115 RAO linking addition.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
