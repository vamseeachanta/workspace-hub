---
name: crossprovider codex acceptance-verdicts-must-be-mechanically-derivab
description: Acceptance verdicts must be mechanically derivable from schema, not prose
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [verdict-propagation, schema-determinism, acceptance-logic]
---

Verdict propagation rules (e.g., 'failed validation forces nonacceptance,' 'warning blocks acceptance') must be encoded as schema fields and aggregation logic, not interpreted prose. Prose alone cannot handle ambiguous cases—e.g., differentiating whether `WARNING` unresolved blocks acceptance while `FAIL` does not.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
