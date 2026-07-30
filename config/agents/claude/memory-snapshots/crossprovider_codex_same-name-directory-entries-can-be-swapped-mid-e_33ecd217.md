---
name: crossprovider codex same-name-directory-entries-can-be-swapped-mid-e
description: Same-name directory entries can be swapped mid-enumeration
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [enumeration, directory-traversal, toctou-safety, verification]
---

Directory enumeration can encounter same-name inode substitution: a file is verified by descriptor, but during traversal the directory entry is renamed away and a different inode installed at the same name. Verify parent directory still names the attested inode before operating on the file.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
