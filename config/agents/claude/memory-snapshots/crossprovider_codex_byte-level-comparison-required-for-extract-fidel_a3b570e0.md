---
name: crossprovider codex byte-level-comparison-required-for-extract-fidel
description: Byte-level comparison required for extract fidelity
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [extract-validation, encoding-sensitivity, office-extracts]
---

Text-mode CSV comparison misses CRLF encoding differences between source binaries and committed extracts. Validate extract fidelity with SHA256 digests and byte-for-byte comparison, not text-mode equality.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
