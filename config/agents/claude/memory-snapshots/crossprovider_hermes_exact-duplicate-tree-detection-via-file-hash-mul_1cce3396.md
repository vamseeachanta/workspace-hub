---
name: crossprovider hermes exact-duplicate-tree-detection-via-file-hash-mul
description: Exact-duplicate tree detection via file-hash multiset creates false positives
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hashing, data-structure, duplicate-detection]
---

Classifying duplicate folders using only a multiset of file hashes (counts/lengths, not paths) causes different tree structures with the same blobs to be falsely classified as exact duplicates. Tree-structure hash must include relative paths, not just blob hashes, to detect true duplicates.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
