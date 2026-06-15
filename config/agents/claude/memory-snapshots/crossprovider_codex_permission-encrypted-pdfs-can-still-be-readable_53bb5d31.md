---
name: crossprovider codex permission-encrypted-pdfs-can-still-be-readable
description: Permission-encrypted PDFs can still be readable
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [extraction, encryption, pdf-handling]
---

RC4 permission-encrypted PDFs with no user password can be decrypted with `authenticate("")` in PyMuPDF. Check extractable text before downgrading to metadata-only stub. Only true password-locked PDFs get metadata-only treatment.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
