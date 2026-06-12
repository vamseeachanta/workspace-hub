---
name: crossprovider hermes tool-mapping-requires-semantic-validation-not-ne
description: Tool mapping requires semantic validation, not nearest-fit assignment
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [audit, tool-normalization, semantic-matching]
---

When normalizing unmapped tool names across providers, validate semantics (arguments, result patterns) before mapping. search_file_content→Grep was safe (grep-style args + result msgs). ask_user was unsafe (interactive input, not file/search/edit action); leave unmapped if no clear fit rather than forcing into available category.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
