---
name: crossprovider codex lazy-dimension-derivation-preserves-empty-ledger
description: Lazy dimension derivation preserves empty-ledger contracts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [schema-design, contracts, ledger-patterns]
---

Schema ledger designs that promise empty results on detailed runs must compute dimensions lazily, not eagerly. Forced derivation violates the contract even when the dimensions are never used.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
