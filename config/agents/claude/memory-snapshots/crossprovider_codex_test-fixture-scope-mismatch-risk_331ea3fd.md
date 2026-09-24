---
name: crossprovider codex test-fixture-scope-mismatch-risk
description: Test fixture scope mismatch risk
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, fixtures, integration-testing, external-data]
---

Unit tests may pin local fixtures (e.g., 12-field CORES list) that don't match live external sources (e.g., workbook). Tests passing against fixture ≠ live correctness. Verify both: fixture-based unit tests AND integration tests using live source.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
