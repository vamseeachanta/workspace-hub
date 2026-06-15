---
name: crossprovider codex corpus-provenance-defects-are-distinct-from-extr
description: Corpus provenance defects are distinct from extraction fidelity
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [corpus-review, provenance, page-accuracy]
---

A batch can pass byte-for-byte re-extraction checks but still fail if page text references non-committed parallel sources (e.g. claiming quotes from 'Exec Summary' when those quotes are actually in a superseded prior draft). Audit page claims against ONLY the committed extracts; flag any phrase that comes from a parallel/non-ingested document as provenance error, not extraction error.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
