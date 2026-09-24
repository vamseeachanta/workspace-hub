---
name: crossprovider codex configuration-verification-tests-must-validate-e
description: Configuration verification tests must validate exact state, not subsets
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, verification, contracts, configuration]
---

Tests verifying canonical configuration must assert all keys (owned and forbidden), order, duplicates, and exact values. Using set operations or partial validation defeats the contract; drift passes undetected when only subsets are checked.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
