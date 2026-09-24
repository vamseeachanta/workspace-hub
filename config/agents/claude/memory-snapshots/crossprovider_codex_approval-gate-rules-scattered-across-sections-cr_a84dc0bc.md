---
name: crossprovider codex approval-gate-rules-scattered-across-sections-cr
description: Approval gate rules scattered across sections create contradictions
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [specification-gaps, approval-gates, contradictions]
---

When degraded runs are described as "may emit reports" in one section and "do not satisfy approval gates" in another, the verdict rule is still ambiguous. Approval logic must be defined once, normatively, covering all scenarios (smoke tests, dry-run, scheduled publication). Ambiguity defeats testing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
