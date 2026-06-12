---
name: crossprovider gemini wave-based-migration-for-large-file-sets-300-fil
description: Wave-based migration for large file sets (300+ files)
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [migration, risk-mitigation, scaling]
---

For multi-repo consolidation (e.g., 5500-file digitalmodel specs), pilot on smallest corpus first (293-file worldenergydata), capture checksums and inventory deltas, validate parity and pointer integrity, THEN scale to larger repos. Skipping pilot results in silent path mapping errors on first production wave.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
