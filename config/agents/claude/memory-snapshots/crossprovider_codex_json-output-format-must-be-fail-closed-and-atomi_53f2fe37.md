---
name: crossprovider codex json-output-format-must-be-fail-closed-and-atomi
description: JSON output format must be fail-closed and atomically one parseable object
metadata:
  type: reference
  source: codex
  bridged: 2026-07-10
  tags: [output-contracts, JSON, testing]
---

Mixing parseable JSON with plain-text instructions on the same stdout stream, or omitting required fields, creates undetectable contract violations. Tests must verify output parity (one object, all required fields, no trailing text), not trust source claims. Format verification is essential when output feeds downstream parsing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
