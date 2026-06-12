---
name: crossprovider gemini index-md-as-source-of-truth-pre-generate-never-s
description: INDEX.md as source of truth: pre-generate, never scan files for listing
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [indexing, performance, work-queue]
---

Work queue listing should read pre-generated INDEX.md, not scan individual files. Regenerate after any mutation (add, archive, status change, priority change). Fast (<2s for 100+ items) and prevents stale views.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
