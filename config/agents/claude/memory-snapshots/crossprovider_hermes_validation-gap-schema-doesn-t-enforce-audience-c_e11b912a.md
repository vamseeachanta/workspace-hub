---
name: crossprovider hermes validation-gap-schema-doesn-t-enforce-audience-c
description: Validation gap: schema doesn't enforce audience_classification against residency
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [schema-validation, consistency-checking]
---

Schema has audience_classification (client-private, etc.) and output_residency (public_llm_wiki, etc.) as independent fields with no cross-validation. Bundle passes with output_residency=public_llm_wiki + audience_classification=client-private, a logical conflict. Add rule: if audience_classification=client-private then output_residency ≠ public_llm_wiki.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
