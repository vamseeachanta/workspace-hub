---
name: crossprovider codex symlinks-in-committed-paths-can-leak-private-con
description: Symlinks in committed paths can leak private content to public artifacts
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [public-safety, path-traversal, symlinks]
---

Path-based filtering cannot isolate public content when symlinks exist in the traversal path. Symlinks can point outside approved directories and leak private/absolute paths into generated metadata. Must explicitly reject symlinks via readlink() checks or symlink-aware path normalization (os.path.realpath vs os.path.abspath), not rely on path suffix matching alone.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
