---
name: crossprovider codex schema-field-mapping-bugs-pass-tests-with-synthe
description: Schema field mapping bugs pass tests with synthetic data
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing-patterns, data-contracts, integration-tests]
---

When multiple code paths read from the same data structure (e.g., JSONL index), inconsistency in field names (`name` vs `symbol`) can pass tests if tests use synthetic data. Fix: normalize schema on load, or add schema-validation tests that use real index rows.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
