---
name: crossprovider codex encrypted-pdfs-enforce-metadata-only-stubs-regar
description: Encrypted PDFs enforce metadata-only stubs regardless of extractable text
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [wiki-ingest, pdf-handling, drm-policy]
---

DRM-protected PDFs (RC4, FOPN, etc.) that pdftotext can read must still be treated as metadata-only stubs under the hardened ingest contract, never full extraction. This is a non-negotiable boundary enforced for legal/license compliance, despite technical feasibility of text recovery.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
