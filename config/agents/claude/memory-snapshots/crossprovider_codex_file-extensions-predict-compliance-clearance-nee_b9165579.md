---
name: crossprovider codex file-extensions-predict-compliance-clearance-nee
description: File extensions predict compliance/clearance need
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [public-safety, source-classification, compliance]
---

Corpus scan shows .json (1.4M), .pdf (290K), .dwg (234K), .ipt (130K) files dominate — CAD formats, vendor PDFs, and data exports all require vendor/private/standards clearance before public ingest. Extension profile is a fast governance signal; bulk ingestion workflows should classify by extension type first, then by source-family.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
