---
name: crossprovider codex schema-contract-mismatch-as-silent-failure-defec
description: Schema-contract mismatch as silent-failure defect class
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [schema-validation, contract-testing, renderer-mismatch]
---

Plans and skills that define data schemas without validating them against actual downstream consumers (renderers, parsers, validators) cause silent failures or malformed output. Codex review of calculation-methodology skill found section YAML schemas documenting richer structures than the renderer consumes — users following the guidance produce invalid YAML or silently lose data.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
