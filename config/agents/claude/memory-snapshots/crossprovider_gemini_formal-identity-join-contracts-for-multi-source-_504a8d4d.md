---
name: crossprovider gemini formal-identity-join-contracts-for-multi-source-
description: Formal identity join contracts for multi-source data systems
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [data-join, identity-contract, multi-source]
---

Establish canonical `sha256:<64hex>` as the join key. Accept `md5:` on reads but never for positive matching. Mark unresolved identity as a distinct status, not a false coverage gap, to avoid silent failures during migrations.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
