---
name: crossprovider codex static-corpus-walk-guards-detect-scope-creep-ear
description: Static corpus-walk guards detect scope creep early
metadata:
  type: reference
  source: codex
  bridged: 2026-06-21
  tags: [testing, privacy, static-analysis]
---

Tests that verify 'this script does NOT read the source corpus' by checking stderr/file-ops patterns are effective early-warning guards. They should whitelist only intentional data sources (tracked JSONL, report JSON, etc.) and fail if new corpus reads appear. This prevents silent expansion of data exposure.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
