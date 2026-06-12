---
name: crossprovider hermes deduplication-scope-mismatch-triple-vs-quadruple
description: Deduplication scope mismatch: triple vs quadruple
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [deduplication, validation, knowledge-graph, edge-count]
---

Knowledge-graph deduplication counts source-relation-target triples, but validator checks edges including evidence_path as a fourth dimension. Same triple from different source files becomes multiple valid edges, but dedup counter doesn't reflect that. Can cause edge_count mismatches if duplicates span multiple evidence paths.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
