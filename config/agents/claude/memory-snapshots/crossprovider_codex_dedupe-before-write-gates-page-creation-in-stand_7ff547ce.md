---
name: crossprovider codex dedupe-before-write-gates-page-creation-in-stand
description: Dedupe-before-write gates page creation in standards ingest
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [ingest, dedupe, standards, llm-wiki]
---

Before creating a new standards page, grep the target domain's standards/ and sources/ for an existing page on the same code_id or title. If found, augment the existing page in place (add missing sections/tables); do NOT create a duplicate or overwrite wholesale. This is a load-bearing gate in the hardened ingest workflow.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
