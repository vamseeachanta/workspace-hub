---
name: crossprovider codex decimal-context-edge-cases-at-exponent-boundarie
description: Decimal context edge cases at exponent boundaries
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [decimal-context, edge-cases, numeric-edge]
---

Test around decimal context `Emax` boundary when hardening numeric normalization, as trailing-zero stripping in `Decimal.normalize()` can produce very large positive exponents that trigger context overflow. This is a residual hardening concern even after precision fixes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
