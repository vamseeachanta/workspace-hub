---
name: crossprovider codex personal-pii-documents-skip-without-ocr-add-to-s
description: Personal/PII documents skip without OCR; add to skip queue instead
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [ingest, pii, scope, skip-queue]
---

Government ID scans (passports, driver licenses), personal reference letters, utility bills, and property documents are out of scope for standards ingestion. Add them to `_skipped.csv` with reason and optionally to the #135 vision queue. Do NOT OCR or process them into the corpus.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
