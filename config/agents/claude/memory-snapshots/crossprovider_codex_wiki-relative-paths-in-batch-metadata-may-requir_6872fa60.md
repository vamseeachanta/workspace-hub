---
name: crossprovider codex wiki-relative-paths-in-batch-metadata-may-requir
description: Wiki-relative paths in batch metadata may require translation to repo-root
metadata:
  type: reference
  source: codex
  bridged: 2026-06-21
  tags: [wiki-repos, path-resolution]
---

Issue tables and batch metadata in wiki-based repos may use paths relative to wiki-root, not repo-root. Verify by checking whether stated paths exist; if not, check under `wikis/<subdir>/` structure before treating paths as broken.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
