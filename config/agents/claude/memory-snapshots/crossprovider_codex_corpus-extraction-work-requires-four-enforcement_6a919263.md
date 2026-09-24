---
name: crossprovider codex corpus-extraction-work-requires-four-enforcement
description: Corpus extraction work requires four enforcement tiers: taxonomy, citation routing, coverage/retrieval validation, and artifact-specific secret scanning
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [corpus-ingest, governance, validation, security]
---

Plans claiming 'no raw paths in outputs' are insufficient; each artifact type (frontmatter, logs, datasets, verification queues, summaries) must have explicit scan rules and named test functions. Generic clauses can pass while specific rows still leak `/mnt/` prefixes or private tokens.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
