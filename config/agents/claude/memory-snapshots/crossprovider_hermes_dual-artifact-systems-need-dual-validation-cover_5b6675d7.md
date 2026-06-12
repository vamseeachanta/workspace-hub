---
name: crossprovider hermes dual-artifact-systems-need-dual-validation-cover
description: Dual-artifact systems need dual validation coverage
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [validation-gaps, dual-artifacts, machine-readable]
---

When generating both human-readable (Markdown) and machine-readable (JSON) artifacts, validation rules must cover both. Llm-wiki #75: public-safety validator scanned report text for forbidden paths/secrets but not JSON summary contents, allowing private-path leakage in the machine-readable artifact. Single-artifact validation is insufficient.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
