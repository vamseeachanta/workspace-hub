---
name: crossprovider codex interface-contracts-must-include-concrete-specif
description: Interface contracts must include concrete specifications
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [specification, interface-design, divergence-prevention]
---

Vague specs like 'reads X, outputs Y' consistently led to divergent implementations across reviews. Contracts must specify: input format with examples, output format, error handling policy, edge case behavior (missing data, unknown values, multi-source scenarios), and exit codes. Without these, implementations diverge in exactly the ways discovered during review.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
