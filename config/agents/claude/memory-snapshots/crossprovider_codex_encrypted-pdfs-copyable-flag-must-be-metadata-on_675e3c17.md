---
name: crossprovider codex encrypted-pdfs-copyable-flag-must-be-metadata-on
description: Encrypted PDFs (copyable flag) must be metadata-only stubs
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [llm-wiki, ingest, encryption, license]
---

Even if encrypted-copyable (RC4 copy-ok flag), full-page extraction violates license constraints. Create metadata-only stub with code_id, title, publisher, revision, source_pdf, license_status: encrypted-metadata-only. Raw PDF stays off-repo; never extract full pages from encrypted PDFs even if pdftotext works.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
