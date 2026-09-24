---
name: crossprovider codex three-tier-data-routing-for-client-wikis
description: Three-tier data routing for client wikis
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-handling, client-wikis, privacy-firewall, llm-wiki]
---

When processing client material: raw documents remain in their original controlled locations; client-specific processed knowledge routes to `llm-wiki-<client>` repositories; only deduplicated, de-identified, and generalized knowledge routes to central `llm-wiki`. This pattern prevents proprietary information leakage while building reusable knowledge assets and enforces privacy firewall discipline.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
