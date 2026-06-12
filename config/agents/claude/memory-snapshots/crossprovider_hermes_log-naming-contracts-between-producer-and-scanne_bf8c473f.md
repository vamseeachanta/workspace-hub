---
name: crossprovider hermes log-naming-contracts-between-producer-and-scanne
description: Log naming contracts between producer and scanner must be explicit
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [observability, logging, contracts, cron]
---

Cron/health scanners looking for log patterns like 'cron-*.log' produce false negatives when producers write 'parity-review-*.md'. Require explicit contract enforcement or documentation; implicit contracts silently break during evolution.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
