---
name: crossprovider codex checksum-validation-with-path-normalization-for-
description: Checksum validation with path normalization for structure changes
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [migration-verification, checksums, path-normalization, integrity]
---

When verifying integrity across directory-structure migrations, use checksums (sha256) with normalized paths (strip source prefix, strip target prefix). This detects silent content loss even when source and target paths differ, catching cases where files are expected but silently dropped.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
