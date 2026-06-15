---
name: crossprovider codex raw-pdfs-stay-off-repo-reference-by-path-only-in
description: Raw PDFs stay off-repo; reference by path only in metadata
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [ingest-contract, compliance, raw-pdfs]
---

The hardened contract mandates that raw vendor PDFs remain under /mnt/ace/O&G-Standards/... and are NEVER committed to the repo. Pages reference them via source_pdf metadata field (relative path, e.g., 'ISO/my-standard.pdf'). This separates vendor IP from derived knowledge artifacts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
