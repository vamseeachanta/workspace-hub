---
name: crossprovider codex pymupdf-authenticate-unlocks-permission-encrypte
description: PyMuPDF authenticate("") unlocks permission-encrypted PDFs without user password
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [pdf-extraction, mechanical-ingest, fitz, encryption]
---

Most permission-encrypted PDFs in the O&G standards collection use RC4 with no user password set. Call `doc.authenticate("")` after `fitz.open()` to unlock these for text extraction. This pattern replaces LLM-based extraction when models refuse copyrighted text, keeping extraction deterministic and local.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
