---
name: crossprovider codex backup-and-deduplication-tools-delete-unchanged-
description: Backup and deduplication tools delete unchanged candidates; timestamp advance does not guarantee a save
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [backup-tools, deduplication, tmux-resurrect, timestamp-semantics]
---

When a backup tool generates a candidate snapshot and finds it byte-identical to the previous version, it deliberately deletes the candidate. Timestamp updates in metadata can advance even when the snapshot is discarded, creating an illusion of work. Verify actual file presence in the target directory, not timestamp metadata.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
