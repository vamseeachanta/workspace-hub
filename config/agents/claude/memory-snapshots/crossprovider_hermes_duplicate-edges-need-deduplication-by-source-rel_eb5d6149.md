---
name: crossprovider hermes duplicate-edges-need-deduplication-by-source-rel
description: Duplicate edges need deduplication by (source, relation, target, evidence_path) tuple
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [deduplication, edge-model]
---

When same concept links via both markdown and wikilink, generator emits two edges with different source-locators but same relation+target. Deduplication key must be (source_family, relation, target, evidence_path) not just (relation, target). If duplicates exist, `duplicate_edge_count` in summary must reflect truth; hardcoding 0 masks the problem.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
