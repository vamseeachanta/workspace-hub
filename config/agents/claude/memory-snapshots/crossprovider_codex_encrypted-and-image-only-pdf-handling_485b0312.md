---
name: crossprovider codex encrypted-and-image-only-pdf-handling
description: Encrypted and image-only PDF handling
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [encrypted-docs, image-only, pdf-routing]
---

Encrypted/DRM PDFs → metadata-only stub (title, code_id, publisher, revision, source_pdf off-repo, license_status: encrypted-metadata-only), not a full page. Image-only scans with no extractable text → skip immediately and append to vision-queue CSV; don't create near-empty pages. Both patterns preserve audit trail without bloat.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
