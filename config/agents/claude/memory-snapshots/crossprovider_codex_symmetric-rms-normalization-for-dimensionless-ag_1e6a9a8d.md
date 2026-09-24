---
name: crossprovider codex symmetric-rms-normalization-for-dimensionless-ag
description: Symmetric RMS normalization for dimensionless agreement gates
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [numerical-methods, agreement-thresholds, dimensionless-metrics]
---

For comparing solver results without unit dependence or benchmark thresholds, normalize as `abs_rms / sqrt((mean(a²)+mean(b²))/2)`. This is dimensionless, solver-order invariant, and avoids synthetic magic numbers.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
