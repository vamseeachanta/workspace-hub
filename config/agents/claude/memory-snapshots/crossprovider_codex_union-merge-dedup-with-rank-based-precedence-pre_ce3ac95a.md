---
name: crossprovider codex union-merge-dedup-with-rank-based-precedence-pre
description: Union-merge dedup with rank-based precedence prevents silent data loss
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-integrity, queue-merging, deduplication]
---

When git merge=union creates duplicate rows (e.g., 38,680 → 17,935), dedupe by logical identity (code_id/table_id/source_pdf/page/csv_path) with rank-based precedence (flagged=3 > no-csv=2 > ok=1 > blank=0) so benign buckets never hide flagged entries. Update write conditions to trigger on dedup activity independently from triage.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
