---
name: crossprovider hermes privacy-schema-validation-requires-cross-field-c
description: Privacy schema validation requires cross-field consistency, not independent field constraints
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [schema-validation, privacy-gates, fail-closed-design]
---

Fail-closed privacy behavior requires validator rules that prevent contradictory combinations: e.g., public residency + client-private audience, internal-note source relabeled as public, source_class_mix inconsistent with actual sources. Checking each field independently still permits privacy leaks when combinations are poisonous. Adversarial tests must cover these contradiction cases.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
