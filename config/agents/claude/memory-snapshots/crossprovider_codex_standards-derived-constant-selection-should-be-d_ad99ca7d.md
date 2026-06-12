---
name: crossprovider codex standards-derived-constant-selection-should-be-d
description: Standards-derived constant selection should be dynamic with auditable choice rationale
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [standards, selection-logic, engineering]
---

Hardcoded enumerated selections (e.g., OCIMF curve A9/A10/A11) should instead apply a documented rule (geometry fit, water-depth bucket) at runtime and record rejected alternatives. Tests that lock hardcoded choices prevent validation of the selection logic. Approved plans requiring 'nearest available' or 'documented selection' are violated by hardcoded paths.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
