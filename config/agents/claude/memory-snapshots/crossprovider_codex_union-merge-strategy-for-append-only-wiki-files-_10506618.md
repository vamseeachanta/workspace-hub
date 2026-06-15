---
name: crossprovider codex union-merge-strategy-for-append-only-wiki-files-
description: Union-merge strategy for append-only wiki files during conflict resolution
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [merge, git, csv, deduplication]
---

For CSV files (_verification-queue, _skipped, vision-queue), keep one header + union all unique data rows (dedupe identical rows). For index.md and log.md, merge all table rows/log entries and recalculate page_count/source_count totals. Report row counts (ours/theirs/merged) as proof of correctness; merged count must be >= max(ours, theirs).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
