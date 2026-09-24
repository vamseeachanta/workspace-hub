---
name: crossprovider codex shared-dataset-directories-clobber-table-invento
description: Shared dataset directories clobber table inventories when multiple source PDFs write to same target
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [standards-ingest, dataset-management]
---

When four riser PDFs each extract tables to `datasets/abs-gui-123/`, only the last writer's inventory survives. Generate a combined manifest that merges table counts across all source PDFs, or use per-source subdirectories to preserve isolation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
