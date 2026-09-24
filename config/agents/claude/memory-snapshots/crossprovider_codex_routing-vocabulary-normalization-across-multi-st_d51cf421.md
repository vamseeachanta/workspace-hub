---
name: crossprovider codex routing-vocabulary-normalization-across-multi-st
description: Routing vocabulary normalization across multi-stage pipelines
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-governance, multi-stage-orchestration, vocabulary-control]
---

Multi-wave or multi-stage ingestion requires a single normalized enum for routing decisions (e.g., public/private/metadata-only/excluded) and separate enum for lifecycle states. Mismatches between stages cause downstream validators to reject or accept incompatible routing states. Define the enum at the pipeline start, not in child stages.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
