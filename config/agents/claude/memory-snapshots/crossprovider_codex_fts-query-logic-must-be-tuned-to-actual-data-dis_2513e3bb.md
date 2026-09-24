---
name: crossprovider codex fts-query-logic-must-be-tuned-to-actual-data-dis
description: FTS query logic must be tuned to actual data distribution
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [search, fts, multi-token-queries, data-dependency]
---

Implicit AND in multi-token full-text search can fail against real data (returns empty). Explicit OR with all-tokens-present bonus, or quoted-token OR merging, is needed when query cardinality is high or data has many repeated tokens. Verify query behavior against actual data, not test fixtures, during planning.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
