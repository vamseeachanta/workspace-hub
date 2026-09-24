---
name: crossprovider codex architecture-contract-enforcement-requires-coord
description: Architecture contract enforcement requires coordination across schema, tests, and docs
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, contracts, documentation, coordination]
---

Changes to an architecture contract (e.g., execution manifest checksum gating) must update all three: the schema (syntax gate), the test helper (semantic gate), and the contract documentation (explain both gates). A single-piece change leaves the contract incomplete and unclear to future implementers.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
