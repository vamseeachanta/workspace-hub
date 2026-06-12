---
name: crossprovider hermes private-client-data-requires-sanitization-promot
description: Private/client data requires sanitization promotion gate before public llm-wiki
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [data-governance, data-boundaries, public-safety]
---

Raw private/client data never routes directly to public llm-wiki; a mandatory promotion gate (llm-wiki-data-promotion-gates.md) sanitizes content, removing client IDs, raw paths, credentials, and unsourced claims. Private derivatives route to llm-wiki-private or client-private targets only. Bypassing this gate is a public-safety failure.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
