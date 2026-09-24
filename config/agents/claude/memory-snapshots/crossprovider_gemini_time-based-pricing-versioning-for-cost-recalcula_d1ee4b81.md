---
name: crossprovider gemini time-based-pricing-versioning-for-cost-recalcula
description: Time-based pricing versioning for cost recalculation
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [cost-tracking, pricing-versioning, time-versioned-data, architectural-pattern]
---

Static pricing configs become stale when API rates change. Add effective_from timestamp to each rate model; when recalculating historical costs, use the rate active at transaction time, not current rate. Prevents cost mis-attribution when provider prices increase or decrease (WRK-1069 cross-review finding: static pricing.yaml causes accuracy drift on older logs).

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
