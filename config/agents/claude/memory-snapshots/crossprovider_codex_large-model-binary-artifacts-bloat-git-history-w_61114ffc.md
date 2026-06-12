---
name: crossprovider codex large-model-binary-artifacts-bloat-git-history-w
description: Large model/binary artifacts bloat git history without LFS tracking
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [git-maintenance, lfs-config, repo-growth]
---

4.8MB JSON model files committed as plain text create large git blobs that persist in history forever, slowing clones/operations. Use Git LFS (or .gitattributes) for all binary/large data files; configure early before repo proliferates.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
