---
name: crossprovider codex pytest-class-scoped-fixtures-don-t-cross-sibling
description: pytest class-scoped fixtures don't cross sibling class boundaries
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [pytest, fixture-scoping, non-obvious-behavior]
---

A fixture defined with class scope inside TestCashFlowComponents is invisible to sibling test classes (e.g., TestProductionAPI12CashFlowMethods) in the same file. Class boundaries are hard scope limits; promote fixtures to function scope or conftest.py for cross-class visibility.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
