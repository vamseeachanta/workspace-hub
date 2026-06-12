---
name: crossprovider hermes baseline-delta-contract-pattern-for-periodic-rep
description: Baseline/delta contract pattern for periodic reports
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [reporting, metrics, baseline-tracking, contract-pattern]
---

For weekly/periodic reports, track previous baseline by loading prior artifact with matching schema/version and date, compute deltas from prior totals, and emit `baseline_run_date` in output for future runs. Enables accurate trend tracking and delta columns without re-scanning history.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
