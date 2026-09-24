---
name: crossprovider codex numeric-validation-pattern-corrected-summary-art
description: Numeric validation pattern: corrected summary artifacts must match authoritative ledger counts before commit
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation-pattern, artifact-reconciliation, data-integrity]
---

When reconciling stale summary markdown (e.g., resource-intelligence-maturity.md) against canonical YAML ledgers, validate that numeric counts (total items, coverage percentages, done/remaining split) match before committing. This prevents summary drift and catches copy-paste errors or stale hand-edited sections that diverge from their sources.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
