---
name: crossprovider codex pdf-encryption-permission-state-must-be-verified
description: PDF encryption/permission state must be verified locally
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [pdf-handling, metadata, verification]
---

Encryption status and copy permissions cannot be determined from catalog metadata alone. Use `pdfinfo` and `pdftotext` verification before classifying sources as metadata-only; extractable PDFs labeled metadata-only due to catalog assumptions create false scope gaps.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
