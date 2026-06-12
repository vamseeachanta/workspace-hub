---
name: crossprovider hermes machine-baseline-collectors-must-redact-credenti
description: Machine baseline collectors must redact credential patterns, not just tokens
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [credential-safety, collectors, redaction]
---

Collectors running `gh auth status` and system commands must redact both full tokens AND partial credential-key patterns (token=..., password=..., secret=...) since command echoes can leak partial values.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
