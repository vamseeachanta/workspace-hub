---
name: crossprovider codex encrypted-pdfs-create-metadata-only-stubs-not-fu
description: Encrypted PDFs create metadata-only stubs, not full pages
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [pdf-ingest, hardened-contract, encryption]
---

PDFs with DRM/encryption (even copy-permitted) create only title/code_id/publisher metadata-only stub in target domain. Mark license_status: encrypted-metadata-only. Full text extraction forbidden; do not attempt workarounds.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
