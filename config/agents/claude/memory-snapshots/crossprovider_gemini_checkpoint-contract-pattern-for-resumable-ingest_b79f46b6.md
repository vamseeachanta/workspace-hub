---
name: crossprovider gemini checkpoint-contract-pattern-for-resumable-ingest
description: Checkpoint contract pattern for resumable ingest processes
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [ingest-patterns, resumability, state-management]
---

Long-running processes (API pulls, file ingestion) store state atomically at Tier 2 (/mnt/ace/.checkpoints/) with schema including: title, edition_date, last_completed_section, sections_total, status, last_error. Resume reads checkpoint, skips completed sections, continues from next. Tested for atomicity, resume noop, edition bumps.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
