---
name: crossprovider hermes fail-closed-design-requires-explicit-boundary-va
description: Fail-closed design requires explicit boundary validation, not default assumptions
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [safety-gates, validation, fail-closed]
---

In #2740 orchestrator, initial implementation allowed --execute without readiness file (returning {status:pass} for None) and accepted arbitrary machine labels without registry validation. Fail-closed gates must validate against canonical sources: read git status --porcelain directly, load readiness evidence from files, cross-check machine labels against config/workstations/registry.yaml. Don't trust caller-supplied flags or defaults.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
