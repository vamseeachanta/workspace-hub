---
name: crossprovider codex schema-inheritance-across-issues-must-be-explici
description: Schema inheritance across issues must be explicit, not assumed
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [planning, cross-issue-dependencies, schema-governance]
---

Child issues that consume parent schemas cannot assume they inherit parent constraints or field definitions. Promised output fields like `coverage_class` and `duplicate_risk` must be explicitly defined in the parent schema or fail-closed; hoping fields will 'be allowed' causes scope drift.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
