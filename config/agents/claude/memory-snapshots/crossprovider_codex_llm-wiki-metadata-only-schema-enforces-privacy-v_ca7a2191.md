---
name: crossprovider codex llm-wiki-metadata-only-schema-enforces-privacy-v
description: llm-wiki metadata-only schema enforces privacy via aggregation thresholds
metadata:
  type: reference
  source: codex
  bridged: 2026-06-19
  tags: [llm-wiki, privacy, schema-design]
---

Generated artifacts disallow raw identifiers, paths, and content beyond a minimum aggregation threshold (3 for client/archive abstractions). Enforced via schema validator and `legal-sanity-scan.sh --diff-only` pre-commit gate.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
