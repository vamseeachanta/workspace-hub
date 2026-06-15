---
name: crossprovider hermes llm-wiki-raw-boundary-protection-requires-explic
description: llm-wiki raw-boundary protection requires explicit reserved-phrase guards, not generic disclaimers
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [llm-wiki, raw-data-boundary, scope-protection]
---

Blanket "no source copying" statements fail to catch project-specific facts or metadata leakage from `/mnt/ace`; need explicit reserved-phrase/identifier patterns like #2612 uses. For batches creating platform entities (e.g., `flng.md`, `fpso.md`), vague heuristics don't prevent drift into SESA/Woodfibre/ACMA/lng-a project-bound content.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
