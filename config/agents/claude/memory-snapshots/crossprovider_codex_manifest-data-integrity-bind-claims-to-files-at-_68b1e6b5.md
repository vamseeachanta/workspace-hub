---
name: crossprovider codex manifest-data-integrity-bind-claims-to-files-at-
description: Manifest/data integrity: bind claims to files at validation time
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [data-integrity, validation]
---

Validators that accept checksums, file sizes, or paths without immediately verifying existence, size match, or checksum correctness hide silent data corruption. Verify claims against actual files in the validation phase, not as a separate offline step.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
