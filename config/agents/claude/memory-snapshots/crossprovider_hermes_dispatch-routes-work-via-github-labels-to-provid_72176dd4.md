---
name: crossprovider hermes dispatch-routes-work-via-github-labels-to-provid
description: Dispatch routes work via GitHub labels to provider-machine lanes with durable ledger tracking
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [dispatch, github-labels, hermes, control-plane, routing]
---

Multi-machine dispatch mechanism uses GitHub issue labels (machine:*, agent:*, status:*, priority:*, cat:*, domain:*) as routing determinants to dedicated per-machine throughput lanes. A durable dispatch ledger artifact (docs/ops/*-dispatch-ledger.md format) tracks issue→provider→machine→validation. Execution gates on plan-approval status.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
