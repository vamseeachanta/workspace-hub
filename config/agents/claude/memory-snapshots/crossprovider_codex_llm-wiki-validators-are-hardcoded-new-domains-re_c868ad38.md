---
name: crossprovider codex llm-wiki-validators-are-hardcoded-new-domains-re
description: llm-wiki validators are hardcoded; new domains require explicit updates
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [llm-wiki, validation, domain-architecture, registry]
---

Adding a new domain to llm-wiki requires manual updates to hardcoded validator whitelists, query-surface registry in `data/query_sources.json`, and public-graph artifact regeneration. Query surface is registry-gated, not file-presence-triggered, so new domains remain invisible to queries until explicitly registered.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
