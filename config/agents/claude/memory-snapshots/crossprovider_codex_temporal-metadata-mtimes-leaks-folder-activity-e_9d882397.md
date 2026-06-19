---
name: crossprovider codex temporal-metadata-mtimes-leaks-folder-activity-e
description: Temporal metadata (mtimes) leaks folder activity even when bucketed
metadata:
  type: reference
  source: codex
  bridged: 2026-06-18
  tags: [metadata-privacy, temporal-leakage, llm-wiki-cleanup]
---

Bucketed mtime values (`latest_mtime_bucket`) were rejected from #731 as privacy-leaking metadata, then the #732 plan attempted to reintroduce them without a governance rule. Bucketing does not eliminate the privacy leak of folder freshness/recency; temporal metadata should require explicit approval and a clear 'when allowed' criterion before use.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
