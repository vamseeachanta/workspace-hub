---
name: crossprovider codex hard-validators-for-schema-invariant-checks-outp
description: Hard validators for schema/invariant checks outperform soft review
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation, testing-strategy, verification]
---

When schema invariants (e.g., "no rule-manager-route in final artifacts" or "all rows have required fields") are checked only in tests/review, they slip past verification. Hard validators (scripts) that block/fail on invariant violations catch defects earlier and more reliably than manual review. Sessions 6-7 identified field gaps and status-leakage defects in generated artifacts that tests alone missed.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
