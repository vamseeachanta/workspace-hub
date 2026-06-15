---
name: crossprovider codex wiki-index-maintenance-concept-duplicates-across
description: Wiki index maintenance: concept duplicates across index
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [wiki-structure, index-maintenance, data-integrity]
---

When updating a concept row in a wiki index, search the full index for stale duplicate rows targeting the same concept page. Updates at one line don't auto-remove old entries elsewhere. Use dedup/consistency checks in tests or during maintenance sweeps to avoid split-brain routing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
