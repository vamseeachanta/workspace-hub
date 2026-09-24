---
name: crossprovider codex slug-based-deduplication-fails-on-generic-filena
description: Slug-based deduplication fails on generic filenames across collections
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [deduplication, reconciliation, hazards]
---

Using filename slugs for deduplication (e.g., toc.md, start.md, author.md) causes many-to-one collisions when the same names appear across different collections/years. Deduplication must use full path or collection-scoped identity, not normalized filenames.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
