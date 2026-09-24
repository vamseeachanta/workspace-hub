---
name: crossprovider codex independent-extract-verification-requires-extern
description: Independent extract verification requires external tools
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [verification, extraction, methodology]
---

When verifying text extracts from binary formats (.msg, .xls), use external tools (not the producer's extractor) with deterministic conventions (header+body) to enable exact matching and avoid circular verification. Parse independently to catch faithfulness issues.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
