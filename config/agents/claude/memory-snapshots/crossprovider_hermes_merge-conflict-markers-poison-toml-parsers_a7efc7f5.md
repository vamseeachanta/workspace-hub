---
name: crossprovider hermes merge-conflict-markers-poison-toml-parsers
description: Merge conflict markers poison TOML parsers
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [merge-conflict, toml, data-validation, quirk]
---

Unresolved merge conflicts in TOML files (<<<HEAD ... ===== ... >>>) make files unparseable even after marker stripping. Duplicate sections (e.g., two [project] blocks) prevent TOML parsing and silently mask dependencies. Validate for merge markers before parsing.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
