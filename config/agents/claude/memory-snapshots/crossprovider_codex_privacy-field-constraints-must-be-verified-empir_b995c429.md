---
name: crossprovider codex privacy-field-constraints-must-be-verified-empir
description: Privacy field constraints must be verified empirically against outputs
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [privacy-validation, policy-enforcement, llm-wiki]
---

Source-title aliasing policy forbids filename/relative_path in reports, but this is not inherited by tools—DNV manifest generator explicitly emits these fields despite repo policy. Schema validation tests must assert forbidden-field rejection, not assume parent policy enforcement.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
