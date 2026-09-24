---
name: crossprovider codex source-body-read-scope-must-be-explicitly-author
description: Source-body read scope must be explicitly authorized in plans
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [planning, read-boundary, scope-creep, authorization]
---

Plans that involve file fingerprinting or metadata extraction never define whether local byte-stream hashing, content-level comparison, or text extraction are allowed. Omitting explicit read-boundary authorization creates implementation ambiguity and risks silent scope creep (e.g., plans forbid ingest/upload but never explicitly authorize or forbid local hashing).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
