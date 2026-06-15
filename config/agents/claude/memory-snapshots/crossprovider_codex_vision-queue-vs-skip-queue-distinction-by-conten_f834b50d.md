---
name: crossprovider codex vision-queue-vs-skip-queue-distinction-by-conten
description: Vision-queue vs skip-queue distinction by content value
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [vision-queue, skip-queue, image-only, triage]
---

Skip queue (_skipped.csv): non-technical personal/admin/property docs, image-only with no value. Vision queue (issue-135-vision-queue.csv): image-only PDFs with potentially technical content that needs OCR/vision. The split is whether the image content is engineering-domain-relevant; if unclear, route to vision for expert judgment rather than assume skip.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
