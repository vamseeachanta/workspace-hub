---
name: crossprovider gemini benchmark-regression-thresholds-must-be-high-to-
description: Benchmark regression thresholds must be high to avoid false positives
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [benchmarking, ci-reliability, threshold-tuning]
---

Use >20% slowdown threshold (not 5%) to distinguish real performance regressions from variance noise. Benchmark timing varies naturally; low thresholds trigger spurious CI failures and reduce signal-to-noise.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
