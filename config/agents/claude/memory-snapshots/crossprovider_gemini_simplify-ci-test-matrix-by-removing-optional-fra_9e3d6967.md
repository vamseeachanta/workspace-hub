---
name: crossprovider gemini simplify-ci-test-matrix-by-removing-optional-fra
description: Simplify CI test matrix by removing optional frameworks
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [ci, simplification, testing]
---

Remove pytest plugins (pytest-mock, pytest-json-report) and extra linters (black, isort, mypy) when core tests run reliably with minimal dependencies. Reduces maintenance surface and CI fragility without sacrificing coverage. Ruff for linting + pytest for tests is often sufficient.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
