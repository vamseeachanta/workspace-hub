---
name: crossprovider codex wave-based-migration-with-per-batch-commit-const
description: Wave-based migration with per-batch commit constraints reduces large-file-count risk
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [migration, batching, governance, risk-isolation]
---

Consolidating 1000+ files from multi-repo specs requires dividing into waves (small corpus first, then large) with per-batch limits (max 500 files, one commit per batch, mandatory checkpoint). This isolation strategy makes partial failures diagnosable and rollbacks tractable rather than ecosystem-wide.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
