---
name: crossprovider hermes dispatch-policy-must-fail-closed-on-contractual-
description: Dispatch policy must fail closed on contractual readiness gates
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [dispatch, readiness, fail-closed, security]
---

Documentation claiming 'data access verified' or 'missing data blocks dispatch' is a load-bearing contract. If readiness can emit only `warn` status and dispatch policy accepts it anyway, the gate is fail-open despite documentation. Inspect policy evaluators for `warn`-accepting code paths; test with live registry entries where checks fail but status remains dispatchable.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
