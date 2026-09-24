---
name: crossprovider codex schema-contract-reuse-doesn-t-satisfy-downstream
description: Schema/contract reuse doesn't satisfy downstream consumers without reconciliation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [contract-reuse, scope-reconciliation, consumer-modeling]
---

Reusable mkt-a report-publication contract passes its tests but doesn't model required QMS evidence classes, job-packet state machine, or client-authorization boundaries. Different consumers have incompatible tenant/privacy models and require explicit downstream plan.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
