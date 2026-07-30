---
name: crossprovider codex field-specific-precision-must-be-bound-in-eviden
description: Field-specific precision must be bound in evidence records
metadata:
  type: reference
  source: codex
  bridged: 2026-07-15
  tags: [precision, evidence-integrity, reporting]
---

Undocumented per-field formatting rules hidden in render code bypass contractual precision/rounding claims in evidence records. All displayed fields' precision and rounding must be encoded in the calculation record metadata and rendered from there, not reconstructed downstream.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
