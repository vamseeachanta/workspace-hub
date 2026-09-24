---
name: crossprovider codex union-merge-driver-for-append-only-shared-files-
description: Union merge driver for append-only shared files in llm-wiki
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-merge, append-only, llm-wiki, union-driver]
---

Uses `.gitattributes merge=union` for wikis/**/wiki/index.md, log.md, _verification-queue.csv, _skipped.csv, issue-135-vision-queue.csv to auto-resolve concurrent additions. Post-merge verification requires checking row counts from both merge parents and deduplicating identical entries to confirm no rows were dropped.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
