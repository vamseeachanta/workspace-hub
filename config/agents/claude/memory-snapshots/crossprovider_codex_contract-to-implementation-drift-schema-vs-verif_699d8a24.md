---
name: crossprovider codex contract-to-implementation-drift-schema-vs-verif
description: Contract-to-implementation drift: schema vs. verifier field enforcement divergence
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [gate-design, contract-mismatch, verification-gap]
---

WRK-1029 exposed that verify-gate-evidence.py checks only `completion_status`, `top_p1_gaps`, and `skills.core_used` count, but resource-intelligence schema lists 12 required fields including wrk_id, generated_at, domain.problem. When schema marks fields required without verifier checks, the contract is overstated and silent gate bypass occurs. Require verifier checks or explicit WARN emission for each schema field.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
