---
name: crossprovider codex partial-fixes-leave-edge-cases-vulnerable-advers
description: Partial fixes leave edge cases vulnerable; adversarial testing must cover shape + value
metadata:
  type: reference
  source: codex
  bridged: 2026-07-04
  tags: [testing, adversarial, completeness]
---

A fix that rejects empty field-counts may still accept malformed field-count objects if tests only cover happy paths (valid vs. invalid) not shape mismatches (wrong keys, type errors). After fixing r1 findings, run adversarial probes for each dimension: shape corruption, value range, type confusion, and cross-field consistency, not just happy-path and null-edge.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
