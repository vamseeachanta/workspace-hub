---
name: crossprovider codex dedupe-by-code-id-title-prevents-duplicate-wiki-
description: Dedupe by code_id+title prevents duplicate wiki pages
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [dedupe, ingest, wiki]
---

Before creating a new wiki page, grep the target domain's standards/ and sources/ directories for an existing entry by code_id and title. If found, augment in place (add missing sections/tables); never overwrite wholesale or create a duplicate. Report every dedupe hit and the action taken.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
