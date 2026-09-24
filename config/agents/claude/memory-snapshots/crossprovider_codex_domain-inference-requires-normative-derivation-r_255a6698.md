---
name: crossprovider codex domain-inference-requires-normative-derivation-r
description: Domain inference requires normative derivation rules
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, schema, determinism]
---

When a plan infers categorical state from path/frontmatter (e.g., wiki domain from file path or metadata), the derivation rule must be explicit with precedence order, normalization examples, and collision behavior. Pseudocode-only functions without concrete mappings leave classification non-deterministic.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
