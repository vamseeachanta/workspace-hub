---
name: crossprovider codex data-row-traceability-fields-are-non-optional
description: Data row traceability fields are non-optional
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-validation, auditability]
---

In regulatory/standards matrices, every row must carry owning_issue, workflow_id, workflow_route, and source_locator fields. Tests must verify these are never null or missing; absence breaks audit trails and makes row provenance unrecoverable.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
