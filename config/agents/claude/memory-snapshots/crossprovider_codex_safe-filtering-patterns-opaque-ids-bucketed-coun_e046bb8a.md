---
name: crossprovider codex safe-filtering-patterns-opaque-ids-bucketed-coun
description: Safe filtering patterns: opaque IDs + bucketed counts, no body reads
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [safety-pattern, privacy, filtering]
---

To keep artifacts repo-safe while preserving categorization, use opaque routing IDs (digests, hashes, sequence numbers) with bucketed counts/extensions, and never include raw file paths or document bodies. Private path/name maps belong outside the repo; published artifacts stay abstract.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
