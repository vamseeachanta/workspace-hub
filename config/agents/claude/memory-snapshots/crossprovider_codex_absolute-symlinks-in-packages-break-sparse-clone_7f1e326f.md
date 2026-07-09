---
name: crossprovider codex absolute-symlinks-in-packages-break-sparse-clone
description: Absolute symlinks in packages break sparse clones
metadata:
  type: reference
  source: codex
  bridged: 2026-07-05
  tags: [package-structure, sparse-clone, symlinks]
---

Absolute paths in tracked symlinks break sparse clones and are anomalous in package structure. When fixing compatibility shims, convert or remove symlinks to enable sparse checkout.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
