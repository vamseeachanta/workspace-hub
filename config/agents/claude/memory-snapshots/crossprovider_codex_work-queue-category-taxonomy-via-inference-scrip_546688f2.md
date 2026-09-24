---
name: crossprovider codex work-queue-category-taxonomy-via-inference-scrip
description: Work queue category taxonomy via inference script
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [metadata-structure, work-queue, taxonomy]
---

Work queue items should include `category:` and `subcategory:` fields, inferred via `scripts/work-queue/infer-category.py` during Stage 1 capture. This enables downstream filtering and routing based on work type.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
