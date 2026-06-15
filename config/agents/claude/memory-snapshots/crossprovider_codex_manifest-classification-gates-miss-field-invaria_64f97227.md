---
name: crossprovider codex manifest-classification-gates-miss-field-invaria
description: Manifest classification gates miss field invariants, only check one condition
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [llm-wiki, manifest-builders, classification, validation-gaps, test-gaps]
---

Manifest builders validate single fields (e.g., `source_role == candidate`) but ignore required companion fields (`extraction_status`, `page_disposition`, `target_domain`). A candidate row can be malformed and still pass, and a support row can be promoted if another support row is compliant. Require exact tuple validation: all required fields must satisfy their contract simultaneously.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
