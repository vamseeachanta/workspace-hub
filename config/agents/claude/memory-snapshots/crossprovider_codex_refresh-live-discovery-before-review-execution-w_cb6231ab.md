---
name: crossprovider codex refresh-live-discovery-before-review-execution-w
description: Refresh live discovery before review/execution when plan is based on snapshot
metadata:
  type: reference
  source: codex
  bridged: 2026-06-21
  tags: [planning, discovery]
---

If a plan was based on a stale snapshot (e.g., 61 items when live tree now has 63), run bounded live discovery before advancing to review/approval. Small drift can mask new high-value items or deprecation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
