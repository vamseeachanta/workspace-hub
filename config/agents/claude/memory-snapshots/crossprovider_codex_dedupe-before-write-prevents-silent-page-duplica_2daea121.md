---
name: crossprovider codex dedupe-before-write-prevents-silent-page-duplica
description: Dedupe-before-write prevents silent page duplicates
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [llm-wiki, ingest, dedupe]
---

Before creating standards pages, grep target domain's standards/ + sources/ for existing page by code_id + title. If found, augment in place (add missing sections) — never overwrite or duplicate. Skipping this gate produces silent duplicates and loses prior revisions; report every dedupe hit with action taken.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
