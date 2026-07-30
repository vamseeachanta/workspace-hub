---
name: crossprovider codex fail-closed-decisions-when-data-is-missing
description: Fail-closed decisions when data is missing
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [design, testing, procurement]
---

In modeling, testing, and procurement contexts with incomplete ground truth, default to 'insufficient evidence' or explicit fail-closed criteria rather than interpolating/averaging/guessing. Benchmarking decisions, acceptance thresholds, and test assertions should all prefer false negatives over false positives when data gaps exist.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
