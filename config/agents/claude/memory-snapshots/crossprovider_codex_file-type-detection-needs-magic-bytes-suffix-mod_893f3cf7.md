---
name: crossprovider codex file-type-detection-needs-magic-bytes-suffix-mod
description: File type detection needs magic bytes + suffix + mode
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [file-types, validation]
---

Suffix-only detection misses encoded formats (e.g., a `.bz2` file with `BZh` magic or a `.html` starting with binary data). Use magic bytes, file suffixes, and file-mode allowlisting together to validate generated output types.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
