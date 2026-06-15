---
name: crossprovider hermes private-wiki-naming-pattern-for-client-data
description: Private wiki naming pattern for client data
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [multi-tenant, llm-wiki, naming-convention]
---

Use pattern `<client>-projects-llm-wiki` for client-specific private wikis (e.g., `mkt-a-llm-wiki`). Keep separate from public `llm-wiki` and from raw data repos. This prevents accidental cross-client or public data leakage.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
