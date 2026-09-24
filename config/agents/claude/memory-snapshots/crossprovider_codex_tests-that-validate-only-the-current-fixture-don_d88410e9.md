---
name: crossprovider codex tests-that-validate-only-the-current-fixture-don
description: Tests that validate only the current fixture don't prove fail-closed contracts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, correctness, contracts]
---

Tests passing on today's data (e.g., five expected rows) does not prove the code fails closed if the manifest changes (e.g., a sixth NAVSEA row appears, or an expected row disappears). Fail-closed contracts require explicit drift test cases: extra unexpected rows, missing expected rows, cardinality mismatches.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
