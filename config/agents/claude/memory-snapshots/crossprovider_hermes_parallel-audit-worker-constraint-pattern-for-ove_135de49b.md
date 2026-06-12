---
name: crossprovider hermes parallel-audit-worker-constraint-pattern-for-ove
description: Parallel audit worker constraint pattern for overnight batches
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [parallel-work, batch-coordination, overnight-workflows]
---

Coordinating overnight audit/batch work: each worker no implementation/no unbounded downloads/no label changes, each comments only on own issue, unique report artifacts per worker. This constraint pattern prevents conflicts and keeps audit artifacts isolated and traceable.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
