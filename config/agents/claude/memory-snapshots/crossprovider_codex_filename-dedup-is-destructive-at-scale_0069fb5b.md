---
name: crossprovider codex filename-dedup-is-destructive-at-scale
description: Filename dedup is destructive at scale
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [deduplication, data-integrity, indexing]
---

Deduping 1.3M assets by filename alone destroys 1M+ rows (118k case-folded filename groups). Requires cryptographic content hashing; missing hashes mean no safe dedup is possible.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
