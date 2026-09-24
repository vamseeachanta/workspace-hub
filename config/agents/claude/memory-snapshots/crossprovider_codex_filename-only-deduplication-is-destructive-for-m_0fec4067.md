---
name: crossprovider codex filename-only-deduplication-is-destructive-for-m
description: Filename-only deduplication is destructive for multi-phase archives
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-management, deduplication, multi-phase-archives]
---

A 1.3M-row asset catalog can have 118K case-folded filename groups with 1M+ legitimate duplicates across different project phases and source roots. Deduplication by filename alone destroys non-unique files that are valid in different contexts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
