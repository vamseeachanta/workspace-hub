---
name: crossprovider codex multi-stage-data-pipelines-need-atomic-staging-o
description: Multi-stage data pipelines need atomic staging or versioned directories to prevent interleaved failures
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [data-pipeline, atomicity, staging]
---

Raw→normalized→curated pipelines risk stale intermediate manifests when any stage fails. Either stage all outputs before promotion, or use versioned build directories. Partial success leaves data in a mismatched state that is hard to diagnose.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
