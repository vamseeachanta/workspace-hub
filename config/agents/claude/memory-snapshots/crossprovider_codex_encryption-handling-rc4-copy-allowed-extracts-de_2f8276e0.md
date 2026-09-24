---
name: crossprovider codex encryption-handling-rc4-copy-allowed-extracts-de
description: Encryption handling: RC4 copy-allowed extracts despite lock; newer handlers block
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [pdf-extraction, encryption, tooling-quirk]
---

pdfinfo reveals encryption + copy-allowance flag. RC4-encrypted PDFs with copy-allowed extract via pdftotext. Newer handlers (e.g., Poppler's FOPN_foweb blocker) may fail completely. Use pdfinfo flag to decide extraction viability before attempting full extraction.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
