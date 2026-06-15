---
name: crossprovider codex new-knowledge-domains-in-llm-wiki-require-tri-pa
description: New knowledge domains in llm-wiki require tri-partite integration
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [llm-wiki, architecture, domain-routing]
---

Adding docs to llm-wiki requires: (1) domain routing decision (wiki directory structure), (2) query-surface registration (data/query_sources.json + validator tests), (3) discovery enablement (scripts/validate_* coverage). Adding pages alone leaves them undiscoverable and untested.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
