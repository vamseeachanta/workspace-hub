---
name: crossprovider codex corpus-inventory-classification-must-precede-ing
description: Corpus inventory classification must precede ingest design
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [corpus-management, file-classification, implementation-completeness]
---

Raw source roots contain mixed files (PDFs, Office docs, archives, executables, databases, metadata). PDF-only ingest plans silently miss or mishandle non-PDF types. Classification and handling rules for each file type must be explicit in acceptance criteria, not deferred to implementation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
