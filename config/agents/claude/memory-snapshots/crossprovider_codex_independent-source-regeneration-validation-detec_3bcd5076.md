---
name: crossprovider codex independent-source-regeneration-validation-detec
description: Independent source + regeneration validation detects generator asymmetries
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [validation, testing, generators, reproducibility]
---

When validating artifact generators (PPTX enrichment, etc.), independently verify raw source contents (zip package SHA256/size) and regenerated output separately—don't assume idempotency proves correctness. FDAS layer1 review found that regeneration passed (git diff empty) but raw inventory didn't match, catching a misalignment that idempotency checks alone would miss.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
