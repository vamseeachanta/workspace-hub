---
name: crossprovider hermes license-corpus-leakage-needs-tdd-contract-not-pr
description: License-corpus leakage needs TDD contract, not prose-only
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [engineering-workflow, tdd, licensing-boundary]
---

Engineering issues with licensing constraints require explicit RED tests or output-contract assertions, not just prose rules. Issue #2760 flagged that "do not commit extracted coefficient corpora" stated in Phase 0/1 prose lacked a corresponding test validating repo-bound artifacts/sidecars/manifests/HTML do not serialize reusable coefficient tables. Without TDD contract, carve-outs (e.g., "minimal numeric golden values") become back doors.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
