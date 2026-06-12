---
name: crossprovider gemini api-document-ocr-failures-on-ihs-licensed-copies
description: API document OCR failures on IHS-licensed copies
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [api-standards, ocr-hazard, document-extraction, vendor-data]
---

Some API standards provided via IHS licensing (particularly API Std 610 and others from early 2000s) fail OCR completely—entire pages return only metadata timestamps without text. Verify document quality before attempting content extraction; if OCR is total loss, fallback to reference lookup or request fresh copy.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
