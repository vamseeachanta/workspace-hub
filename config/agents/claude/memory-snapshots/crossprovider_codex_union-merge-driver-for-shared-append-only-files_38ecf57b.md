---
name: crossprovider codex union-merge-driver-for-shared-append-only-files
description: Union merge driver for shared append-only files
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [git-workflow, merge-strategy, llm-wiki-ingest]
---

Use git's `merge=union` driver in .gitattributes for shared append-only resources (index.md, log.md, verification queues, CSV logs). Adoption sequence: bring .gitattributes from origin/main onto existing branches before merging. If driver leaves conflict markers, manually union-resolve by keeping all rows from both sides, dedup identical rows, retain one header.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
