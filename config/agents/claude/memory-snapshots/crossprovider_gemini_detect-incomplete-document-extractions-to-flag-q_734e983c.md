---
name: crossprovider gemini detect-incomplete-document-extractions-to-flag-q
description: Detect incomplete document extractions to flag quality issues
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [document-ingestion, quality-gate]
---

Sessions with populated metadata but blank/minimal document content indicate OCR or encoding failures. Implement early detection and flagging to prevent downstream processing of corrupted extracts.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
