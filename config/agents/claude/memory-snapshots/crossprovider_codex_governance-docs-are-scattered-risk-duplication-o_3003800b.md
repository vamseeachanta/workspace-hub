---
name: crossprovider codex governance-docs-are-scattered-risk-duplication-o
description: Governance docs are scattered; risk duplication on new contracts
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [governance, duplication-risk, schema-design]
---

Data pipeline governance is split across operational rules (docs/architecture/), architecture notes (docs/architecture/), governance decisions (docs/governance/), and enforcement rules (.claude/rules/). Before authoring new standards, bounded search across all four to avoid forking existing routing/promotion/ledger contracts. Existing contracts may already define the enums/fields you're about to invent.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
