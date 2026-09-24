---
name: crossprovider codex encrypted-drm-pdfs-remain-metadata-only-stubs
description: Encrypted/DRM PDFs remain metadata-only stubs
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [copyright, drm-handling, policy, metadata-only]
---

Repo policy: PDFs with effective DRM (FOPN, RC4 copy-protection) never become full-text pages, even if pdftotext extracts text. Encrypted documents produce metadata-only resolver stubs (title, code_id, publisher, revision, license_status: encrypted-metadata-only) to avoid licensing liability. Prevents both copyright and tool-trust issues.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
