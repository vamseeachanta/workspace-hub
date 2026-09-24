---
name: crossprovider gemini canonical-identifier-pattern-when-dual-namespace
description: Canonical Identifier Pattern When Dual Namespaces Exist
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [governance, identity, testing]
---

When the same entity has multiple naming surfaces (e.g., frontmatter metadata vs. directory structure), explicitly define which is canonical and enforce it through tests. Omitting this creates silent identity drift and makes deduplication/reconciliation fail unpredictably.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
