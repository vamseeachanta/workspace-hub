---
name: crossprovider codex encrypted-pdfs-with-copy-disabled-are-still-text
description: Encrypted PDFs with copy-disabled are still text-extractable
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [pdf-parsing, encrypted-content, tooling-quirk]
---

pdftotext extracts usable text from RC4-encrypted files marked copy:no in metadata, even though pdfinfo reports encryption. Under hardened contract, treat as metadata-only augmentations not full extractions. Trust extraction tool output over metadata flags for extractability judgment.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
