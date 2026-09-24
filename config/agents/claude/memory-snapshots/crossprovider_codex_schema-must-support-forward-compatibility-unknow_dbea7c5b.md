---
name: crossprovider codex schema-must-support-forward-compatibility-unknow
description: Schema must support forward-compatibility unknowns
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [schema, data-modeling, forward-compatibility]
---

Schemas must represent explicit unknown/TBD states as first-class values (e.g., positive integer | "unknown"), not coercions or placeholders. Blocking when required by the specification prevents silent data loss or downstream validation surprises.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
