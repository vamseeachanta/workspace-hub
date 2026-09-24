---
name: crossprovider codex dependency-consumption-requires-code-proof-not-p
description: Dependency consumption requires code proof, not prose
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [dependencies, contracts, plan-verification]
---

When a plan claims to 'consume' another component's contract (e.g., token grammar, validator function), the consumption must appear in pseudocode, imports, or tests within the plan itself. Prose statements like 'will consume' do not constrain implementation and leave gaps for reimplementation drift.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
