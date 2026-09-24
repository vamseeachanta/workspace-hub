---
name: crossprovider codex two-gate-validation-pattern-for-integrity-critic
description: Two-gate validation pattern for integrity-critical fields
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, testing, validation, schema]
---

Execution manifests use a two-gate pattern: JSON Schema validates syntax (`sha256:<64 hex chars>`), and a pytest semantic verifier computes exact file hashes to reject fabricated digest-looking values. Schema syntax validation alone is insufficient for integrity gates. Apply this when validating checksums, signatures, or other unforgeable evidence.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
