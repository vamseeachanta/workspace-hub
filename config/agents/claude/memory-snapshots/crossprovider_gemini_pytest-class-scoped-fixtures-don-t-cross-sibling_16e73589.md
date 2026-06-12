---
name: crossprovider gemini pytest-class-scoped-fixtures-don-t-cross-sibling
description: Pytest class-scoped fixtures don't cross sibling classes
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [pytest, test-fixtures, python-testing]
---

Fixtures defined at class scope inside one test class (e.g., `config_with_economics` inside `TestCashFlowComponents`) are invisible to sibling classes at the same level (e.g., `TestProductionAPI12CashFlowMethods`). Move fixtures to module or function scope to share across class boundaries.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
