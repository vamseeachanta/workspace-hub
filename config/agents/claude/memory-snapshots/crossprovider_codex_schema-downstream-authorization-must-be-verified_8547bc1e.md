---
name: crossprovider codex schema-downstream-authorization-must-be-verified
description: Schema downstream authorization must be verified
metadata:
  type: reference
  source: codex
  bridged: 2026-06-18
  tags: [schema, contracts, governance]
---

Downstream plans must verify what output classes/fields the schema actually authorizes, not infer from plan prose. Session 5/6: plan claimed `coverage`, `duplicate_risk`, `mapping_confidence`, `organization_quality_signal` fields, but #729 schema only authorized root-level fields and output classes, not pair-level fields. The schema is the contract; ground plan claims in schema definitions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
