---
name: crossprovider codex off-repo-private-data-makes-deterministic-regene
description: Off-repo private data makes deterministic regeneration impossible
metadata:
  type: reference
  source: codex
  bridged: 2026-06-18
  tags: [reproducibility, governance, generated-artifacts]
---

Private maps, configs, or secrets kept off-repo as optional inputs prevent reproducibility: CLI accepts missing private map (#733), runs still emit present/absent status instead of failing closed, and checked-in artifacts can't regenerate without the private data. Accept non-determinism and version artifacts, or track the private data with privacy masking.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
