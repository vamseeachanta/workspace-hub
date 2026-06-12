---
name: crossprovider hermes performance-regression-baseline-pollution
description: Performance regression baseline pollution
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [performance-testing, statistics, regression-detection]
---

When detecting performance regressions, compute baseline mean/std from historical executions **excluding** the current execution being evaluated. If baseline includes the regressed run, the average is diluted and regression factor threshold is underestimated (e.g., 5.0/1.40 vs. 5.0/1.04).

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
