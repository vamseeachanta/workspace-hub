---
name: crossprovider codex copy-allowed-rc4-encryption-permits-text-extract
description: Copy-allowed RC4 encryption permits text extraction via pdftotext
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [pdf-encryption, tool-quirk, extraction]
---

PDFs with RC4 encryption but copy-permission enabled are not extraction-blocked; pdftotext + pdfinfo still work. Process as provisional/raw text, not metadata-only stubs. Extraction-blocked PDFs (no copy permission) → metadata-only resolver instead.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
