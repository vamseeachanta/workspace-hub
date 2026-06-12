---
name: crossprovider hermes baseline-carry-forward-regression-in-v1-v2-audit
description: Baseline carry-forward regression in v1→v2 audit migration
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [audit-schema, regression, baseline-continuity, v2-migration]
---

When extending audit scripts with v2 finding families (content_quality, grouping, size, usage), the baseline/waiver logic must unify all families through one common pipeline, not apply waivers only to legacy findings array. v2-only families never matched prior baselines because they were in separate arrays; fix requires merging or extending `_apply_baseline()` and `_apply_waivers()` to consume all family arrays.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
