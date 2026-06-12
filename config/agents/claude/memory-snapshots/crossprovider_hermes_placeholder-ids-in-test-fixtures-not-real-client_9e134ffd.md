---
name: crossprovider hermes placeholder-ids-in-test-fixtures-not-real-client
description: Placeholder IDs in test fixtures, not real client corpus names
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [privacy, test-fixtures, confidentiality]
---

Hardcoded client corpus IDs (acma-private-wiki, llm-wiki-acma) in generic test fixtures/docs turn scaffolding into client-specific leakage and expose confidential naming. Use safe placeholders (corpus_id: placeholder-xxx, corpus_name: placeholder-yyy) in fixtures; document real-world mapping separately.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
