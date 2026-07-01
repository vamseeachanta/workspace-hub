---
name: crossprovider codex route-lifecycle-vocabularies-must-normalize-to-s
description: Route/lifecycle vocabularies must normalize to single enum across subsystems
metadata:
  type: reference
  source: codex
  bridged: 2026-06-30
  tags: [routing, vocabulary, validator, ingestion-workflow]
---

When ledger, content lanes, storage API, and retrieval system each define their own routing/lifecycle states (e.g., #51: `public_llm_wiki`/`private_sidecar`/`metadata_only`/`excluded_no_ingest`, vs. #52: `ingest`/`metadata_only`/`private_only`/`exclude`), downstream validators disagree. Must define one normalized state enum and map lane-specific terms to it before validator implementation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
