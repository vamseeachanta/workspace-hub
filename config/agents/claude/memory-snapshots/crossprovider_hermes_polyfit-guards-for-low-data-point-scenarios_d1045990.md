---
name: crossprovider hermes polyfit-guards-for-low-data-point-scenarios
description: Polyfit guards for low-data-point scenarios
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [numpy, data-validation, time-series]
---

`np.polyfit` requires ≥2 data points. Single-day timestamp aggregations may produce only 1 row, causing silent NaN warnings or failures. Add length guards before polyfit: skip analysis or use fallback for `len(data) < 2`.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
