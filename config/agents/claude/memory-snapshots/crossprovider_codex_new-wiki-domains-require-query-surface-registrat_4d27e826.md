---
name: crossprovider codex new-wiki-domains-require-query-surface-registrat
description: New wiki domains require query-surface registration before content is discoverable
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [wiki-structure, domain-routing, query-surface, validators]
---

Adding a new wiki domain (e.g., Salesforce) requires: (1) updating `data/query_sources.json` to register the domain, (2) creating/updating domain `llms.txt` manifests, (3) updating validator tests (`scripts/validate_llm_wiki_query_surface.py`, `tests/test_llm_wiki_query_surface.py`). Domain content added before these steps will not be queryable by AI consumers. This is a structural dependency, not optional cleanup.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
