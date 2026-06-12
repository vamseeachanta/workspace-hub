---
name: crossprovider codex llm-wiki-tables-need-parse-status-metadata
description: llm-wiki tables need parse_status metadata
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [llm-wiki, table-policy, parse-status]
---

Every table CSV in datasets/norsok-*/ must have a `parse_status` column with value `provisional-unverified` (parsed semantic) or `raw-unverified` (raw layout). Never generate tables marked `verified` — verification is deferred to a later step. This policy is load-bearing for llm-wiki #122/#124 and decouples data generation from validation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
