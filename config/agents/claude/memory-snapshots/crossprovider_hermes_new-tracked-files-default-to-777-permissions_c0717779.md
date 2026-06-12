---
name: crossprovider hermes new-tracked-files-default-to-777-permissions
description: New tracked files default to 777 permissions
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [file-hygiene, repo-structure, permissions]
---

Scripts that create new files (config, docs, checker code) often default to world-writable mode (rwxrwxrwx). Explicitly set 644 for docs/config, 755 for executables; don't rely on umask defaults.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
