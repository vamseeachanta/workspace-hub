---
name: crossprovider codex union-merge-dedup-pattern-for-rewritten-csvs
description: Union-merge dedup pattern for rewritten CSVs
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [git-merge, dedup, csv, cron-ingest]
---

When git merge=union combines branches that repeatedly rewrite CSVs (e.g., every 6h), duplicates accumulate exponentially. Dedupe on logical identity (code_id/table_id/source_pdf/page/csv_path), rank by structural_status so benign buckets never hide flags (flagged>no-csv>ok>blank). Write only when processing or dedup changed rows.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
