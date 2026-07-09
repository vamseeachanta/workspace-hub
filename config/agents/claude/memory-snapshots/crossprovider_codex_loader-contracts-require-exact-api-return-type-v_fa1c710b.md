---
name: crossprovider codex loader-contracts-require-exact-api-return-type-v
description: Loader contracts require exact API/return-type verification
metadata:
  type: reference
  source: codex
  bridged: 2026-07-07
  tags: [modularity, integration, testing]
---

Reuse of existing loaders (e.g., RegionalCostLoader.get_day_rate()) without verifying exact parameters, return fields, and units (usd_day, clamped, hpht) can silently diverge from plan. Require API contract test before pseudocode.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
