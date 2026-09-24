---
name: crossprovider codex encrypted-but-copyable-pdfs-must-be-metadata-onl
description: Encrypted-but-copyable PDFs must be metadata-only stubs, not full pages
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [standards-ingest, licensing, contract-enforcement]
---

Under HARDENED contract, licensed encrypted PDFs (where pdftotext can read but DRM restricts republishing) become metadata-only stubs with only title/code_id/publisher/revision/source_pdf/license_status fields. Do not extract sections/tables/figures from encrypted sources even if text is readable.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
