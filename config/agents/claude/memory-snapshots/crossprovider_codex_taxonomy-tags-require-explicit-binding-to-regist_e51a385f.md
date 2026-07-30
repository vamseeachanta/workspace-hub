---
name: crossprovider codex taxonomy-tags-require-explicit-binding-to-regist
description: Taxonomy tags require explicit binding to registered sources with version-state separation
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [schema, validation, data-integrity]
---

Generic 'public source' validation is insufficient; must bind tag→source ID, distinguish retrieval-date from source-version-date, and exclude sources marked 'no longer updated.' Public registries can declare staleness—this must fail-closed in schema validation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
