---
name: crossprovider codex bundle-completeness-requires-full-stream-validat
description: Bundle completeness requires full-stream validation, not tar-list-only checks
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [archival, encryption, validation, data-integrity]
---

After creating encrypted/compressed bundles, validating via `tar -tf` (list archive) alone will miss mid-stream corruption in zstd decompression or tar parsing. Full-stream decrypt-decompress-parse validation must complete successfully before declaring a bundle valid, especially for large bundles (>10 GB) where streaming errors are more likely to occur.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
