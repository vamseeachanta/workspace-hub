---
name: crossprovider hermes readiness-evidence-must-carry-source-corpus-dige
description: Readiness evidence must carry source_corpus_digest and fail closed on stale
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [validation, artifact-freshness, llm-wiki, test-driven-development]
---

Artifacts must embed `source_corpus_digest` and validator must recompute current corpus digest and reject mismatches. Freshness validation defaults to repo-root detection when not explicit. This prevents stale artifacts from passing validation after code/schema changes.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
