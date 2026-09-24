---
name: crossprovider codex session-deduplication-required-in-multi-attribut
description: Session deduplication required in multi-attributed cost aggregation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-integrity, cost-tracking, aggregation]
---

When cost-tracking logs attribute the same session to multiple WRKs with identical `cost_usd`, naive summation by WRK then totaling results in double-counting. Reports must provide both attributed totals (per-WRK) and deduplicated totals (unique sessions).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
