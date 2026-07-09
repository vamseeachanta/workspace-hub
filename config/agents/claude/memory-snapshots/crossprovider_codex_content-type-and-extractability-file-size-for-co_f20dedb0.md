---
name: crossprovider codex content-type-and-extractability-file-size-for-co
description: Content type and extractability >> file size for corpus planning
metadata:
  type: reference
  source: codex
  bridged: 2026-07-01
  tags: [ingestion, corpus, classification, triage]
---

When planning bulk LLM corpus ingestion, classify by extension family and extraction type first; file size and count don't predict ingestion value. Large families (e.g., 1.88TB simulation files) often require domain-specific parsers, making their ingestion value much lower than smaller, text-native formats.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
