---
name: crossprovider codex multi-dimensional-test-matrix-proof-completeness
description: Multi-dimensional test matrix proof completeness
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, matrices, verification]
---

Test matrices that classify outcomes (exceptions, error codes, platform behaviors) must cross all relevant dimensions to prove their own rules. A 1D matrix (e.g., options only) cannot verify a 2D classification claim (exception-subclass × errno). Such gaps allow false proofs to pass review.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
