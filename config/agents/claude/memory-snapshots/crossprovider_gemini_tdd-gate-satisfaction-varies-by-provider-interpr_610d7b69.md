---
name: crossprovider gemini tdd-gate-satisfaction-varies-by-provider-interpr
description: TDD gate satisfaction varies by provider interpretation
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [tdd-validation, cross-provider-governance, gate-design]
---

Claude requires explicit red-phase and green-phase commits; Codex reuses pre-existing tests; Gemini accepts dummy echo tests as padding. This reveals a governance gap—the gate definition needs tightening or per-provider variation rules must be documented explicitly.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
