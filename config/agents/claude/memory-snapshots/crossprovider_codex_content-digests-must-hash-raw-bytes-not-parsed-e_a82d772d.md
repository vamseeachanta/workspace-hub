---
name: crossprovider codex content-digests-must-hash-raw-bytes-not-parsed-e
description: Content digests must hash raw bytes, not parsed equivalents
metadata:
  type: reference
  source: codex
  bridged: 2026-07-04
  tags: [validation, digest, csv, hashing]
---

Hashing normalized/parsed CSV (via re-split with commas) collapses delimiter, quoting, and line-ending differences, causing collisions where semicolon-delimited and comma-delimited records with identical parsed values share the same digest. Hash exact source bytes or exact decoded text before parsing; verify different delimiter/encoding variants with same parsed content produce different digests.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
