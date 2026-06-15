---
name: crossprovider codex wiki-page-frontmatter-schema-required-and-prohib
description: Wiki page frontmatter schema: required and prohibited fields
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [wiki, frontmatter, schema]
---

Required fields: `code_id`, `publisher`, `revision`, `jurisdiction`, `visibility: private-llm-wiki`, `source_pdf` (off-repo file reference), `license_status`. Explicitly omit `extraction_policy` and `raw_copy_allowed`. Tables extracted from PDFs go to datasets/_verification-queue.csv with parse_status PROVISIONAL-BY-DEFAULT.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
