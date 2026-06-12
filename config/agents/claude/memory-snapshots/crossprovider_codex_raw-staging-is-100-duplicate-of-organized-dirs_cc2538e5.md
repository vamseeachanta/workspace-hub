---
name: crossprovider codex raw-staging-is-100-duplicate-of-organized-dirs
description: raw/ staging is 100% duplicate of organized dirs
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [corpus-structure, ingest-scope, deduplication]
---

The raw/ directory in O&G-Standards contains complete duplicates of all files in the organized publisher dirs (API, ASTM, etc.). Verified via full content hashing (100% overlap). Always ingest from organized dirs, exclude raw/ to avoid duplication.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
