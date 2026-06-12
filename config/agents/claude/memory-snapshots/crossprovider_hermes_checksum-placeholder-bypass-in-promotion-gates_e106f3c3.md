---
name: crossprovider hermes checksum-placeholder-bypass-in-promotion-gates
description: Checksum placeholder bypass in promotion gates
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [schema-validation, compliance-gates, cryptographic-integrity]
---

Schema validation accepted prose placeholders (e.g., `sha256:contract-checksum-required-at-publication`) when actual SHA-256 hashes were required. Fix: add `pattern: ^sha256:[a-fA-F0-9]{64}$` to schema for `report_eligible: true` fields. Compliance gates must enforce cryptographic validation, not accept prose promises.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
