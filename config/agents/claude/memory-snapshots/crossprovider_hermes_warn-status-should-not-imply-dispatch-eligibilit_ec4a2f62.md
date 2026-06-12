---
name: crossprovider hermes warn-status-should-not-imply-dispatch-eligibilit
description: Warn status should not imply dispatch eligibility despite readiness pass
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [dispatch-semantics, status-contracts, safety-contracts]
---

Dispatch policy and readiness semantics must align: readiness status 'warn' indicates non-fatal issues, not dispatch-eligible. Dispatch selection should only accept status=='pass'. Readiness can mark dispatchable:true for warn status for other consumers, but dispatch policy must explicitly gate on status=='pass', not dispatchable field.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
