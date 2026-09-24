---
name: crossprovider codex row-level-citation-contract-with-structured-fiel
description: Row-level citation contract with structured fields for ingestion
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [citations, data-quality, provenance, ingestion]
---

Require structured citation metadata: source_title, source_url (absolute), page_reference, quoted_text, confidence enum. Freeform `source` strings are insufficient for deterministic duplicate detection. Enables later automated ingestion without re-interviewing data sources.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
