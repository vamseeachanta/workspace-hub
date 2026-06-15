---
name: crossprovider codex filename-case-variants-signal-different-editions
description: Filename case variants signal different editions, not accidental duplicates
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [pdf-handling, deduplication, standards]
---

Case-variant filenames like Append_d.pdf vs append_d.pdf represent different editions with distinct hashes and page counts. Simple filename matching fails; use pdfinfo title + content hash to distinguish real duplicates from edition variants.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
