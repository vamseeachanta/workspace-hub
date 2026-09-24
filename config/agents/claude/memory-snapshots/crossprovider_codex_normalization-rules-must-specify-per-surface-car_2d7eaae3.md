---
name: crossprovider codex normalization-rules-must-specify-per-surface-car
description: Normalization rules must specify per-surface cardinality and composition
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [identity-join, normalization, surface-contracts]
---

When a plan normalizes identities (e.g., bare 64-hex to sha256:hex) for join operations, the rule must be independently specified for each surface (source records vs. wiki pages) and the composition must be explicit. Silent composition (e.g., source normalizes then wiki normalizes differently) produces false-positive coverage that hides as diagnostic-only warnings.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
