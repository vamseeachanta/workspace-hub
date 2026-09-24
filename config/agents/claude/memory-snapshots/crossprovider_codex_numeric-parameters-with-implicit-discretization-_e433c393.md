---
name: crossprovider codex numeric-parameters-with-implicit-discretization-
description: Numeric parameters with implicit discretization or quantization must document the mapping
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [api-design, correctness, documentation]
---

Reviewed code declared density parameters as linear multipliers but implemented logarithmic quantization (producing 4x density from a 2x multiplier). When a numeric API parameter has quantization, discretization steps, or non-linear mapping, explicitly document the transformation in the contract.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
