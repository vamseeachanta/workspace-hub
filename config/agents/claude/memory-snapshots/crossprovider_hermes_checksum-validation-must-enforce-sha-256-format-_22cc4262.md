---
name: crossprovider hermes checksum-validation-must-enforce-sha-256-format-
description: Checksum validation must enforce SHA-256 format, not placeholders
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [schema-validation, artifact-integrity, llm-wiki]
---

Execution manifest schema requires actual SHA-256 hashes (pattern: `^sha256:[a-fA-F0-9]{64}$`) for `report_eligible: true`, not placeholder strings like `sha256:contract-checksum-required-at-publication`. Fixtures must use real hashes computed from artifact files; test regression coverage confirms placeholder rejection.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
