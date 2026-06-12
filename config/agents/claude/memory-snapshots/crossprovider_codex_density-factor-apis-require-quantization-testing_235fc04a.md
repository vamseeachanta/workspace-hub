---
name: crossprovider codex density-factor-apis-require-quantization-testing
description: Density factor APIs require quantization testing
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [testing, api-contracts, math]
---

Mathematical APIs with density multipliers (e.g., mesh refinement factor=2.0) can have non-obvious quantization (e.g., log4 levels producing 4x instead of 2x panels). Contract validation must test exact semantics, not just "produces more output."

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
