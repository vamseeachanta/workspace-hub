---
name: crossprovider hermes adversarial-review-first-pass-can-miss-major-art
description: Adversarial review first pass can miss MAJOR artifact-spec violations
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [review-methodology, artifact-validation, quality-gate]
---

Initial adversarial reviews (e.g., MINOR verdict) can overlook MAJOR issues in generated artifact completeness: missing captions, wrong page dimensions, empty legal transcripts appearing as success. Pattern: add artifact-spec validation to review checklist (page size, caption presence, evidence non-empty) to catch scope violations on first pass.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
