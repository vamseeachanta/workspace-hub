---
name: crossprovider codex self-referential-baseline-bias-in-norm-benchmark
description: Self-referential baseline bias in norm/benchmark calculations
metadata:
  type: reference
  source: codex
  bridged: 2026-07-07
  tags: [statistics, norms, benchmark, bias]
---

When computing a field's metrics vs play baseline using the same source CSV, the field is part of its own denominator, creating high variance at small n and distorted deltas. Requires explicit leave-one-out baseline, n-per-comparator disclosure, or field exclusion from its own baseline comparison.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
