---
name: crossprovider codex producer-consumer-enum-compatibility-must-be-exp
description: Producer↔consumer enum compatibility must be explicit, not deferred as risk
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-contracts, enum-compatibility, integration]
---

Scorecard emits `empty`/`sample`/`full` for freshness_status but plan defines different enum values. This is not a "risk to note"; it requires explicit mapping (scorecard → contract enum transformation) or compatible enum sets with regression tests.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
