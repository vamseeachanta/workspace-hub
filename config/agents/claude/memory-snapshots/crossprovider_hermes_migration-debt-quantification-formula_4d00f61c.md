---
name: crossprovider hermes migration-debt-quantification-formula
description: Migration debt quantification formula
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [metrics, audit, ecosystem-health]
---

Quantify remediable migration debt as `known_migration_debt_per_1k_records = known_migration_debt_reads * 1000 / post_records`. Classify concentration status: 'concentrated' if top_migration_rule_share_pct ≥ 40%, 'mixed' otherwise. Per-provider density varies (Claude 13.20, Gemini 14.28, Hermes 0.00 reads/1k in the April 2026 audit).

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
