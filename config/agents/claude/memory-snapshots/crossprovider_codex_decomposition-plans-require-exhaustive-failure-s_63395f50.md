---
name: crossprovider codex decomposition-plans-require-exhaustive-failure-s
description: Decomposition plans require exhaustive failure-surface coverage, not convenient subsets
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [decomposition-plans, coverage-completeness, acceptance-criteria]
---

Issue #2452: plan identified E722, F841, F541, and broad debt across modules, but child issues (#2467, #2468) only owned an outlier file and safe-rule subset. Remaining rule families had no child issue, no acceptance target, no explicit residual-owner. Adversarial reviews should verify child-issue matrix covers all known failure surfaces with explicit disposition (owned, delegated, residual-owner named).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
