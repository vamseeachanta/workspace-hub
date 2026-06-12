---
name: crossprovider codex synthetic-test-fixtures-inadequate-for-formula-r
description: Synthetic test fixtures inadequate for formula rendering in openpyxl
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [xlsx-extraction, test-fixtures, openpyxl]
---

openpyxl-generated workbooks do not compute formulas and typically do not populate cached results, making them unsuitable for TDD when cached values are part of the pipeline contract. Use committed fixture files with precomputed cached values or handcrafted XML fixtures for formula cell tests.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
