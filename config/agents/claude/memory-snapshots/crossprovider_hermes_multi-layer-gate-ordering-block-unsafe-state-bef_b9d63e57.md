---
name: crossprovider hermes multi-layer-gate-ordering-block-unsafe-state-bef
description: Multi-layer gate ordering: block unsafe state before resource contention
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [gate-ordering, performance, resource-contention]
---

In #2740, dirty-worktree check initially ran after lease-wait, causing unnecessary lock-file sleeps on unsafe checkout. Reordered to check cleanliness (dirty, ahead/behind) before acquiring lease—fail fast on validation, minimize resource waits. Gate order: ambiguity checks → plan/approval → readiness → cleanliness → lease → execution.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
