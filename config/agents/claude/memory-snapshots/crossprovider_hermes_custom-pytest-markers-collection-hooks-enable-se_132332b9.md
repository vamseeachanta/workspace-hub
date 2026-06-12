---
name: crossprovider hermes custom-pytest-markers-collection-hooks-enable-se
description: Custom pytest markers + collection hooks enable selective execution at scale
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [pytest, conftest, markers]
---

coordination/tests/conftest.py (171 lines) demonstrates markers (unit, integration, coordination, slow, agent, memory, external) + pytest_collection_modifyitems hook for filtering. Valuable pattern for large monorepos with diverse test types. Enables `pytest -m unit` or `pytest -m 'not slow'` at scale.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
