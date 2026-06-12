---
name: crossprovider codex frontmatter-schema-migration-is-prerequisite-170
description: Frontmatter schema migration is prerequisite — 170+ pages missing required fields
metadata:
  type: reference
  source: codex
  bridged: 2026-05-27
  tags: [schema-audit, frontmatter-gaps, data-quality]
---

Existing standards pages universally lack `source_pdf`, `license_status`, `visibility`, and `jurisdiction`. Full-fidelity ingest must include schema migration step; do not extend old-schema pages or create new pages without these fields.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
