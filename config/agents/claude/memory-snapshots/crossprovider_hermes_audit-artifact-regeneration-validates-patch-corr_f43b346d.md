---
name: crossprovider hermes audit-artifact-regeneration-validates-patch-corr
description: Audit artifact regeneration validates patch correctness
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [audit-contract, validation-pattern, TDD]
---

When a plan patches audit contract rules, regenerate the audit artifacts (e.g., `analysis/provider-session-ecosystem-audit.json`, `docs/reports/provider-session-ecosystem-audit.md`) and inspect for expected semantic changes only. This catches off-by-one bugs, reference mismatches, and drift in the updated contract.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
