---
name: crossprovider codex encrypted-pdfs-with-copy-text-enabled-are-extrac
description: Encrypted PDFs with copy/text enabled are extractable
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [pdf, encryption, extraction, pdftotext]
---

PDF encryption flag alone doesn't block extraction; if copy/extract permissions are enabled, `pdftotext` succeeds. Check actual text output, not just the encryption flag, before deciding metadata-only.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
