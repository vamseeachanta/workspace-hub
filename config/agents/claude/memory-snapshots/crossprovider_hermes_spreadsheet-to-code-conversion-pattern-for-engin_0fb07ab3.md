---
name: crossprovider hermes spreadsheet-to-code-conversion-pattern-for-engin
description: Spreadsheet-to-code conversion pattern for engineering calculations
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [excel-to-code, engineering-calculations, pytest-pattern]
---

Extract Excel formulas via cell-by-cell JSON dump, create Python module with explicit unit-conversion constants (IN_TO_M, LB_TO_KG, FT_TO_M, etc.), dataclasses for inputs, functions per calculation step, and cell-reference comments (# Source: Sheet, Cell: ref). Verify via pytest with approx() for floating-point. Successfully applied to Ballymore jumper manifold: 18 functions, 81 test cases, all formulas replicated faithfully.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
