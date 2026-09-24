---
name: crossprovider codex mapping-tables-diverge-from-live-data-under-edge
description: Mapping tables diverge from live data under edge cases
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-validation, mapping, edge-cases, scorecard]
---

Contract mapping tables (e.g., scorecard freshness to completeness status) may assume hypothetical value combinations that don't appear in live data, or miss real combinations that do. Validation must run against actual data, not just the table design. Live scorecard data included `missing|runtime_fetched` pairs the plan's table didn't address.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
