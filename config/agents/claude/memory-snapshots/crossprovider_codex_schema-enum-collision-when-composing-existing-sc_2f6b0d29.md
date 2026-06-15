---
name: crossprovider codex schema-enum-collision-when-composing-existing-sc
description: Schema enum collision when composing existing schemas
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [schema-design, composition-risk, contract-mismatch]
---

Composing existing schemas risks silent enum collisions. Example: new plan introduces source_class enum with values like 'public-federal-data', 'vendor-licensed', but existing report-evidence-bundle.schema.yaml already has source_class with incompatible values like 'source-doc-key', 'promotion-ledger-entry'. Reconciliation requires explicit mapping/rename/layering rule before implementation, not 'will compose' claims.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
