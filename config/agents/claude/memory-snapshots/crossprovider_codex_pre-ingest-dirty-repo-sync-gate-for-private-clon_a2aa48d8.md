---
name: crossprovider codex pre-ingest-dirty-repo-sync-gate-for-private-clon
description: Pre-ingest dirty-repo sync gate for private clones
metadata:
  type: reference
  source: codex
  bridged: 2026-05-27
  tags: [git-workflow, ingest-gates, private-repo]
---

Private repo clones behind remote (dirty state, unmerged refs) must be synced and deduped before write-phase ingest. Dirty state blocks implementation as a critical safety/data-integrity checkpoint; prevents commit sweep-contamination.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
