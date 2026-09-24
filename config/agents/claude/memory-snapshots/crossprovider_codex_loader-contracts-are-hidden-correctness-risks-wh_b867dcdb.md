---
name: crossprovider codex loader-contracts-are-hidden-correctness-risks-wh
description: Loader contracts are hidden correctness risks when reused without explicit verification
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [contract-verification, integration-testing, hidden-assumptions]
---

Assuming a reused loader returns expected fields, units, and parameter semantics without verifying its API contract is a common source of silent data mismatches. Explicit tests pinning loader parameters, return types, and units are required before reuse.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
