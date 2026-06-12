---
name: crossprovider hermes validator-recompute-without-threshold-gating-acc
description: Validator recompute without threshold gating accepts failing benchmarks
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [validation-gap, benchmark-integrity, acceptance-criteria]
---

A validator that recomputes artifacts and checks equality to committed state will pass even if the metrics fall below thresholds. Gate must include explicit `metric >= threshold` checks, not just `recomputed == committed` equality.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
