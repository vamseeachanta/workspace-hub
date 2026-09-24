---
name: crossprovider codex frontmatter-schema-drift-creates-audit-debt-migr
description: Frontmatter schema drift creates audit debt; migrate before bulk ingest
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [frontmatter-schema, standards-metadata]
---

Old fields (extraction_policy, raw_copy_allowed) linger; new fields (visibility, license_status, source_pdf, edition_verified) missing from existing pages. Audit entire page set before bulk ingest to identify schema violations. Standardize on single schema per generation rather than adopting incrementally.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
