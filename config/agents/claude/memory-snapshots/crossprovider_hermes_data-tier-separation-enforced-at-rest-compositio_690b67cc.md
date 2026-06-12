---
name: crossprovider hermes data-tier-separation-enforced-at-rest-compositio
description: Data tier separation enforced at rest, composition allowed at runtime
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [data-architecture, tier-separation, client-data, leakage-prevention]
---

Architecture plans must keep public/domain-private/client-private data separated at rest in distinct repositories (e.g., /mnt/local-analysis/<client>-llm-wiki for private client corpora). Composition for insight reports allowed only at retrieval/report runtime. Validation must prevent accidental merging.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
