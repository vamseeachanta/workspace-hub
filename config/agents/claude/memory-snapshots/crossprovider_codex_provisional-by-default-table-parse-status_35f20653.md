---
name: crossprovider codex provisional-by-default-table-parse-status
description: Provisional-by-default table parse_status
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [table-parsing, fidelity-gate, llm-wiki-contract]
---

Every extracted table must have parse_status = provisional-unverified (parsed) or raw-unverified (raw_layout), NEVER verified. Use raw-unverified only when table structure is uncertain (merged cells, collapsed rows). This is the proven NORSOK contract and prevents scale ingests from asserting false fidelity.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
