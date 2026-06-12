---
name: crossprovider gemini sesa-requires-path-canonicalization-for-dedup
description: SESA requires path canonicalization for dedup
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [sesa, data-quality, workflow]
---

SESA corpus (418 files, 1.46 GB) has duplicate/variant paths (Old/, JWhipple/, dated transmittal folders, format-triplets). A path-canonicalization pass must run before extraction to avoid indexing the same asset multiple times.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
