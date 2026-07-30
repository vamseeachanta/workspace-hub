---
name: crossprovider codex three-tier-wiki-data-classification-for-knowledg
description: Three-tier wiki data classification for knowledge ingest
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [documentation, data-governance, architecture]
---

Raw source documents remain in their controlled locations; processed/client-specific knowledge routes to `llm-wiki-<client>` repos; only deduplicated, de-identified, and generalized knowledge enters main `llm-wiki`. This prevents raw/confidential material leakage while enabling knowledge reuse.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
