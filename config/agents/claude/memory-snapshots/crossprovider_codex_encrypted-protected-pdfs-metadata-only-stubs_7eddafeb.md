---
name: crossprovider codex encrypted-protected-pdfs-metadata-only-stubs
description: Encrypted/protected PDFs → metadata-only stubs
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [drm-handling, metadata-preservation, copyright]
---

When copy-protected PDFs are detected (pdfinfo succeeds but extraction is blocked), emit a lightweight metadata-only resolver (code_id, title, publisher, revision, source_pdf, license_status: encrypted-metadata-only) instead of skipping entirely. Preserves provenance and discoverability while honoring DRM.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
