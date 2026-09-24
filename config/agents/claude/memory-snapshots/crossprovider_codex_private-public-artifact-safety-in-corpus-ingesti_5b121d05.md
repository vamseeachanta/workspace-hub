---
name: crossprovider codex private-public-artifact-safety-in-corpus-ingesti
description: Private/public artifact safety in corpus ingestion
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, corpus-ingestion, data-governance, public-private-boundary]
---

When materializing public artifacts (case studies, examples, reports) from private corpus ingestion, require an explicit redaction/tokenization contract BEFORE creation, not as post-hoc validation. Distinguish private raw paths from public-safe tokens/hashes in all schema and outputs. This gate is easy to defer and causes leaks.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
