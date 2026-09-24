---
name: crossprovider codex exact-duplicate-claims-require-byte-level-verifi
description: Exact-duplicate claims require byte-level verification, not name-matching
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [dedup, verification, skills]
---

For skill deduplication (#2290), Codex found only 1 of 7 'exact duplicates' were actually byte-identical; the rest had divergent content despite matching frontmatter names. Always SHA-compare before assuming identical artifacts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
