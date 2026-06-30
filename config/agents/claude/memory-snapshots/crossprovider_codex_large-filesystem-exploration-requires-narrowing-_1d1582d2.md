---
name: crossprovider codex large-filesystem-exploration-requires-narrowing-
description: Large filesystem exploration requires narrowing strategy
metadata:
  type: reference
  source: codex
  bridged: 2026-06-27
  tags: [filesystem-search, exploration-strategy, scaling]
---

When searching large mounts like `/mnt/ace` with mixed datasets, initial broad filename patterns are too noisy. Use extension filters, specific keyword searches, timeouts, and focus on structured-data roots rather than enumerating all matches.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
