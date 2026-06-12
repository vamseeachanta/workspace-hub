---
name: crossprovider gemini static-pricing-table-inaccuracy-for-historical-c
description: Static pricing table inaccuracy for historical cost recalculation
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [pricing, temporal-data, cost-tracking]
---

A frozen pricing.yaml reflects only current rates. Recalculating cost_usd for historical logs using current pricing.yaml will be inaccurate if API prices changed. Store effective_from timestamps in pricing records; use historical rates matched to log timestamp, not current rates.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
