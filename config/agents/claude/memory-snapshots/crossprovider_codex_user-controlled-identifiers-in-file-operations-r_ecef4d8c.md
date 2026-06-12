---
name: crossprovider codex user-controlled-identifiers-in-file-operations-r
description: User-controlled identifiers in file operations require sanitization
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [security, file-io, path-traversal]
---

Imported geometry workflows frequently use user-provided names as identifiers; when these names are used directly in filename construction, path traversal is possible (e.g., mesh.name = '../../outside' escapes output_dir). Sanitize at the boundary where user input enters file operations.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
