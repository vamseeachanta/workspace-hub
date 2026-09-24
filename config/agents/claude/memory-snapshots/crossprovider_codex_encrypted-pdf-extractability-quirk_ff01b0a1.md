---
name: crossprovider codex encrypted-pdf-extractability-quirk
description: Encrypted PDF extractability quirk
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [pdf-tooling, encryption, extractability]
---

pdftotext often succeeds despite copy-disabled encryption flags (PDF tooling quirk). Check both pdfinfo (encryption status) and actual pdftotext output; encrypted files become metadata-only stubs, not full pages.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
