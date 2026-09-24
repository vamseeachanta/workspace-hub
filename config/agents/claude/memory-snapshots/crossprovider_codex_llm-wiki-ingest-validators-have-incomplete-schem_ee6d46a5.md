---
name: crossprovider codex llm-wiki-ingest-validators-have-incomplete-schem
description: llm-wiki ingest validators have incomplete schema coverage
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [llm-wiki, validation, data-contracts]
---

Validators in data pipelines (readiness_matrix.py, routing_queue.py) check enum values and isolated fields but miss dict-key safety, cross-field consistency, and full invariants. Each validator is locally sound but doesn't enforce the complete row contract. Expand validators to enforce full schema, not piecemeal concerns.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
