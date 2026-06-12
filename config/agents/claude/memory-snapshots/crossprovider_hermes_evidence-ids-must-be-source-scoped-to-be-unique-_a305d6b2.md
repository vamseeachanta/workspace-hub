---
name: crossprovider hermes evidence-ids-must-be-source-scoped-to-be-unique-
description: Evidence IDs must be source-scoped to be unique across inventories
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [evidence-tracking, cross-repo-traceability, metadata-design]
---

When `relative_evidence_id` is derived only from file path (not source), identical relative paths under different source roots get identical evidence IDs even if file contents differ. Downstream tooling that cross-references evidence becomes ambiguous. Solution: always pair evidence IDs with `source_id`; never assume evidence ID uniqueness without source context.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
