---
name: crossprovider codex exact-duplicate-classification-requires-byte-lev
description: Exact-duplicate classification requires byte-level verification
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [deduplication, hygiene, verification]
---

Audit findings labeling skill/code pairs as 'exact duplicates' must be validated with sha256/byte-level comparison, not just frontmatter-name matching. Only 1 of 7 'exact-duplicate' pairs studied was actually byte-identical; the other 6 had divergent content requiring manual diff/merge before deletion.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
