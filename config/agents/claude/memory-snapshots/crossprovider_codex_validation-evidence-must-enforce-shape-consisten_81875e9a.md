---
name: crossprovider codex validation-evidence-must-enforce-shape-consisten
description: Validation evidence must enforce shape consistency, not just presence
metadata:
  type: reference
  source: codex
  bridged: 2026-07-04
  tags: [validation, proof, edge-case, testing]
---

Checking `ragged_rows` truthiness without validating entry shapes and cross-checking against observed row counts allows malformed probe evidence to pass. Validate field-count consistency, type-check evidence objects, regex-validate digest hex, and require explicit sidecar/convention state; test malformed shapes (wrong row numbers, unknown keys, type mismatches), not just empty vs. non-empty.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
