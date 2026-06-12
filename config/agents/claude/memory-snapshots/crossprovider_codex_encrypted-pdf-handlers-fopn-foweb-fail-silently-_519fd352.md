---
name: crossprovider codex encrypted-pdf-handlers-fopn-foweb-fail-silently-
description: Encrypted PDF handlers (FOPN_foweb) fail silently; treat as inaccessible
metadata:
  type: reference
  source: codex
  bridged: 2026-05-27
  tags: [pdf-processing, encryption, standards-ingest]
---

Proprietary DRM handlers like FOPN_foweb cause pdftotext/pdfinfo to fail or return garbage. Mark PDFs as 'inaccessible-drm' and defer ingest until manual verification. Never infer edition/metadata from filename when PDF tools fail.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
