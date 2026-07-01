---
name: crossprovider codex use-manifest-index-files-instead-of-filesystem-c
description: Use manifest/index files instead of filesystem crawls for large shares
metadata:
  type: reference
  source: codex
  bridged: 2026-06-30
  tags: [inventory, audit, performance]
---

When auditing a large directory tree, prefer machine-readable manifests (assets.json, .jsonl indices) over recursive filesystem scans. Manifests provide accuracy and speed; direct crawls hit performance limits on large mounts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
