---
name: crossprovider hermes benchmark-baselines-must-include-10-15-buffer-ab
description: Benchmark baselines must include 10-15% buffer above minimum
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [benchmarking, testing, monitoring]
---

Baselines set at observed minimum create false positive regressions due to system load variance. Set baseline at ~1.3x expected minimum to absorb normal fluctuation without triggering alerts. Prevents alert fatigue.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
