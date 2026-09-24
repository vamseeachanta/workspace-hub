---
name: crossprovider codex section-scoped-validators-prevent-accidental-pat
description: Section-scoped validators prevent accidental pattern matches
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validator-design, parsing, scope-safety]
---

Validators that scan for all instances of a pattern (markdown links, table rows, issue tokens) without section scoping can accidentally match content in unrelated sections. Validators meant to validate a specific document section should limit their scanning scope to that section.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
