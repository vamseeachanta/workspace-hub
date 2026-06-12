---
name: crossprovider codex implementation-contracts-must-be-explicit-not-ge
description: Implementation contracts must be explicit, not generic shapes
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [contract-design, interface-specification, implementation-safety]
---

Plans describing interfaces as generic JSON shapes (e.g., `{warnings, criticals, findings, score?}`) lead to incompatible implementations. Required fields, field types, severity semantics, decision rules (e.g., 'what is an improvement?'), and failure behavior must be concrete before implementation begins. Leaving these to 'later docs' is a MAJOR blocker.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
