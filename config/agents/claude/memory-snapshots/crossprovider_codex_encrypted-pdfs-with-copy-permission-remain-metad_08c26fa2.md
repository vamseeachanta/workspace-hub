---
name: crossprovider codex encrypted-pdfs-with-copy-permission-remain-metad
description: Encrypted PDFs with copy permission remain metadata-only
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [encrypted-pdf, licensing, metadata-only-stubs]
---

RC4 encryption with 'copy allowed' permission flag still blocks full extraction under the hardened ingest contract for licensing conservatism. Create metadata-only stubs (title, code_id, publisher, revision, source_pdf, license_status: encrypted-metadata-only), never full extracted pages, even if pdftotext succeeds.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
