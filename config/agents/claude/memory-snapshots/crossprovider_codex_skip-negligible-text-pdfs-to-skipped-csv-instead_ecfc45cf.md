---
name: crossprovider codex skip-negligible-text-pdfs-to-skipped-csv-instead
description: Skip negligible-text PDFs to _skipped.csv instead of creating empty pages
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [wiki-quality, content-filter]
---

PDFs with <5 KB extractable text (usually copyright footers/image-only scans) should go to _skipped.csv for vision queue rather than become near-empty wiki pages. Prevents wiki pollution and flags images for manual decision downstream.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
