---
name: crossprovider codex two-gate-validation-pattern-for-promotion-eligib
description: Two-gate validation pattern for promotion-eligible evidence
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [schema-validation, semantic-gates, promotion-gating]
---

JSON Schema gates syntax/structure only; pytest semantic verifiers must compute exact evidence (SHA-256 hashes, file residency, legal-scan results) and reject fabricated/omitted entries. Tests must cover both gates and their interaction. Schema syntax validation alone is insufficient for promotion-gated content.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
