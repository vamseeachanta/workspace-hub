---
name: crossprovider codex unextracted-metadata-databases-block-git-promoti
description: Unextracted metadata databases block Git promotion
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [data-governance, privacy, git-safety]
---

SQLite databases with missing content_hash and anonymized_title fields (extraction_status=pending) cannot be versioned in Git. Require read-only adapters that emit sanitized aggregates only, never raw paths/titles/client identities.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
