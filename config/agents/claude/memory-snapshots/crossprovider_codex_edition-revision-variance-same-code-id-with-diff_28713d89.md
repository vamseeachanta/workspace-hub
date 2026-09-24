---
name: crossprovider codex edition-revision-variance-same-code-id-with-diff
description: Edition/revision variance: same code_id with different edition year = separate pages
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [standards-ingest, versioning, deduplication-edge-case]
---

When multiple revisions exist (e.g., ISO 14919 unversioned vs ISO 14919:2001), grep includes edition variance. Same code_id + different edition year = separate canonical pages, not duplicates. Prevents conflation of superseded versions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
