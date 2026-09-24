---
name: crossprovider codex checksum-with-path-normalization-detects-migrati
description: Checksum-with-path-normalization detects migration completeness across moves and renames
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [verification, checksums, migration, integrity]
---

Comparing `sha256sum` output with `sed`-normalized paths (stripping source/target prefixes before diff) catches file moves and renames that simple file-count parity would miss, providing stronger post-apply confidence in content preservation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
