---
name: crossprovider hermes governance-implementation-plan-creep-via-undersp
description: Governance-implementation plan creep via underspecified artifact contract
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [plan-architecture, governance-drift, artifact-contract]
---

Parent governance plan (#2280) repeatedly absorbed implementation detail intended for child issue (#2281). Risk: artifact contract gaps (stable keys, ordering rules, delta semantics left as open policy) cause implementation to drift from plan once code resolves policy unilaterally. Lock contract before implementation starts.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
