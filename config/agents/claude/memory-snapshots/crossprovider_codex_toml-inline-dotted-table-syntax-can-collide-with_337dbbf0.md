---
name: crossprovider codex toml-inline-dotted-table-syntax-can-collide-with
description: TOML inline/dotted table syntax can collide with block-form merges
metadata:
  type: reference
  source: codex
  bridged: 2026-08-03
  tags: [toml, merging, syntax-conflict, config-management]
---

When local config has inline form `tui = { animations = false, status_line = [...] }` and canonical sends block form `[tui]`, the inline entry is retained while a new block is appended, causing the staged TOML to reject what was valid local syntax instead of converging while preserving unrelated keys like `animations`.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
