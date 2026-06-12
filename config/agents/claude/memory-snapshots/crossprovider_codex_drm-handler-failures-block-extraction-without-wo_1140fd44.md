---
name: crossprovider codex drm-handler-failures-block-extraction-without-wo
description: DRM-handler failures block extraction without workaround — treat as metadata-only hard block
metadata:
  type: reference
  source: codex
  bridged: 2026-05-27
  tags: [pdf-extraction-hazard, drm-limits, metadata-fallback]
---

Some encrypted PDFs fail pdftotext with specific handlers (e.g., FOPN_foweb security handler). No extraction workaround exists. Treat as metadata-only; do not attempt decryption or guess content. Mark source as unextractable in source ledger.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
