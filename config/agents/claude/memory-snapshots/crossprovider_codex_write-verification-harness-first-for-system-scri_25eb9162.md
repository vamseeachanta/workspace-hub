---
name: crossprovider codex write-verification-harness-first-for-system-scri
description: Write verification harness first for system scripts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [tdd, system-scripts, testing-strategy]
---

For multi-phase system scripts (especially cleanup), implement the `--dry-run` mode first, then write the implementation to make it green at each phase. TDD at system level: Red (dry-run mode), then implement each phase's logic to pass. Harness becomes the living test.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
