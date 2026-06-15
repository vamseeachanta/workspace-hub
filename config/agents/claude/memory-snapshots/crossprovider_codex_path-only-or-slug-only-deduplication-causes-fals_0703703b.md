---
name: crossprovider codex path-only-or-slug-only-deduplication-causes-fals
description: Path-only or slug-only deduplication causes false collision at scale
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [dedup, schema, counting, ingest]
---

Normalizing filenames or paths without collection/year/source context merges different documents. Generic names like `toc.md`, `start.md` collapse dozens of distinct sources. Require full path + metadata keys for identity matching.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
