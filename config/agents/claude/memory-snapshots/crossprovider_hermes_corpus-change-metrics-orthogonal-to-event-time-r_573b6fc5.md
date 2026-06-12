---
name: crossprovider hermes corpus-change-metrics-orthogonal-to-event-time-r
description: Corpus change metrics orthogonal to event-time recency
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [audit, metrics, temporal-logic]
---

Backfills, rebuilds, and re-exports change log volume without corresponding event timestamps. Filtering recent activity by event-time can report zero activity even when corpus changed substantially. Require separate 'corpus reconciliation' metrics (post_record delta, session count delta, file modification times) alongside event-time recent activity to detect and explain divergence.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
