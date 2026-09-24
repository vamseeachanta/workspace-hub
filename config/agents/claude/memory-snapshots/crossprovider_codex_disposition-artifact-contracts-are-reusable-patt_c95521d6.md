---
name: crossprovider codex disposition-artifact-contracts-are-reusable-patt
description: Disposition artifact contracts are reusable patterns for follow-up work
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [contracts, patterns, reuse]
---

Scripts/test suites like `og_standards_document_support_disposition.py` define specific field contracts (routing_id, digest, extension, disposition class, follow-up issue refs, no-ingest/no-read flags) that should be mirrored in new follow-up work rather than invented. These contracts embed the safety boundaries and data model.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
