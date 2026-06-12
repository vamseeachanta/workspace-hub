---
name: crossprovider hermes off-scope-leakage-persists-when-generator-lacks-
description: Off-scope leakage persists when generator lacks scope filter, not validator
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [generator-design, scope-enforcement, data-flow]
---

llm-wiki #77: generator emits `cites` edges from any `sources`/`references` value without checking scope boundaries. Off-scope targets reach artifacts because generator doesn't filter, not because validator is too permissive. Validator fixes alone don't prevent leakage; generator must enforce scope at emission time.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
