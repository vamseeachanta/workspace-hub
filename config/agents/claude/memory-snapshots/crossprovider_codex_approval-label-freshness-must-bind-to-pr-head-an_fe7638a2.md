---
name: crossprovider codex approval-label-freshness-must-bind-to-pr-head-an
description: Approval label freshness must bind to PR head and plan state
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [security, approval-gate, github-api]
---

A label applied before plan rewrite, force-push, or material change can pass as stale approval. Require label applied_at > latest plan artifact commit / PR head SHA / approval-request timestamp. Invalidate on PR synchronize or plan file changes unless a human re-labels.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
