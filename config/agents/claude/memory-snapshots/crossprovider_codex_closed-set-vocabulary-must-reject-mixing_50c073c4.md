---
name: crossprovider codex closed-set-vocabulary-must-reject-mixing
description: Closed-set vocabulary must reject mixing
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [vocabulary-contracts, schema-validation, classification-vocab]
---

Classification schemes (source-extract vs. engineering-screen) have separate closed-set vocabularies. Mixing vocabularies (e.g., analysis_maturity in source-extract fields) enables contract violations silently. Validation must reject inconsistent field sets from different schemes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
