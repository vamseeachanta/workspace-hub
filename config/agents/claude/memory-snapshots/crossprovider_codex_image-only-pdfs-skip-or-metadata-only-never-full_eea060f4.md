---
name: crossprovider codex image-only-pdfs-skip-or-metadata-only-never-full
description: Image-only PDFs: skip or metadata-only, never full page
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [content-filtering, ingest, quality-gate]
---

PDFs with negligible extractable text should be added to `_skipped.csv` plus vision queue (skip) or converted to metadata-only stubs (license_status: encrypted-metadata-only); never create full pages with garbage titles or near-empty content. Sessions 4–6 apply this consistently.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
