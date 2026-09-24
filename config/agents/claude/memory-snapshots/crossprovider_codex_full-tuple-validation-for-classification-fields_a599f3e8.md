---
name: crossprovider codex full-tuple-validation-for-classification-fields
description: Full-tuple validation for classification fields
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [classification-safety, tuple-validation, llm-wiki-manifest]
---

Single-field validation (checking only source_role or extraction_status) misses category promotion defects. Classification state must be validated as a consistent tuple: code_id, source_role, extraction_status, page_disposition, license_class, visibility, target_domain. One mismatched field breaks the invariant silently.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
