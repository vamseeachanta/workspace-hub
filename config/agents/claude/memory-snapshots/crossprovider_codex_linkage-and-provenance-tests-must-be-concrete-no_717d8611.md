---
name: crossprovider codex linkage-and-provenance-tests-must-be-concrete-no
description: Linkage and provenance tests must be concrete, not aspirational
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [testing, provenance, falsifiability]
---

Plans asserting "every record has source_title, source_url, page_reference, quoted_text, confidence" need test code that iterates all records and fails if any field is missing or empty. Weaker language like "page reference or quote support" is too vague to be falsifiable.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
