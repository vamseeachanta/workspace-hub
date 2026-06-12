---
name: crossprovider codex hermes-kanban-idempotency-broken-create-initial-
description: Hermes kanban idempotency broken: create --initial-status blocked then block fails
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [hermes, kanban, idempotency, state-machine]
---

Creating a task with `hermes kanban create --initial-status blocked` then calling `hermes kanban block` fails because Hermes only blocks tasks in `running` or `ready` states; the block appends a comment first, then fails. Tests mock this away, hiding the broken contract. Re-runs are not idempotent and append duplicate comments before failure.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
