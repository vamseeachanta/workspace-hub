---
name: crossprovider hermes provenance-fields-required-in-public-graph-manif
description: Provenance fields required in public graph manifests
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [llm-wiki, public-graphs, provenance, schema]
---

Public graph manifests must include `source_scope`, `source_family`, `source_corpus_digest`, and `backlinks` fields to track data provenance and enforce boundaries. These fields prevent undocumented data promotion from private/raw sources into public graphs. Update both generator and validator field contracts together.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
