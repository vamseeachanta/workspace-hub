---
name: crossprovider hermes duplicate-uniqueness-classification-can-ignore-t
description: Duplicate/uniqueness classification can ignore tree structure and layout
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [data-classification, deduplication, structural-equality]
---

Grouping files for deduplication by only the sorted multiset of content hashes (ignoring relative paths and symlink topology) causes false-positive exact-duplicates. Two directory trees with same file contents but different directory structure, symlink targets, or filenames are labeled `exact_duplicate_tree`. The classification name overstates equivalence; name and structure must factor into grouping.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
