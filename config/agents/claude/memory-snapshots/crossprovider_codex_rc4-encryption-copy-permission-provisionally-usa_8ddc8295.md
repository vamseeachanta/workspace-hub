---
name: crossprovider codex rc4-encryption-copy-permission-provisionally-usa
description: RC4 encryption + copy permission = provisionally usable; FOPN_foweb handler requires OCR route
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [encryption, pdf-extraction, error-handling, tooling]
---

PDFs with RC4 + copy permission enabled allow text extraction via pdftotext (treat as provisional/raw OCR-dense source). Conversely, FOPN_foweb handler errors indicate no native extraction; create metadata-only stub and route to OCR/licensed-viewer (#135). Handle encryption failures distinctly by handler type.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
