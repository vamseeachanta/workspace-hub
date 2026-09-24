---
name: crossprovider codex redaction-is-load-bearing-for-private-path-inven
description: Redaction is load-bearing for private-path inventory
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [redaction, privacy, data-handling]
---

Metadata inventory systems processing private paths (e.g., `/mnt/ace/...`) must ensure all public/repo-tracked output is fully redacted and sanitized. Literal paths, client names, or reconstructable directory trees in summaries violate data-handling contracts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
