---
name: crossprovider hermes stashed-artifacts-may-have-schema-drift-regenera
description: Stashed artifacts may have schema drift; regenerate not reuse
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [artifact-compatibility, schema-drift, llm-wiki, validation]
---

When merging archived/stashed artifacts (e.g., from `llm-wiki-outside-stash-2026-05-18.patch`), verify schema compatibility with the current validator. Old artifacts may use deprecated schema versions (missing fields like `added`, `code_id`, `is_public_safe`, etc.) and must be regenerated from the committed generator rather than simply restored.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
