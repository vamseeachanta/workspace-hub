---
name: crossprovider codex input-contract-enforcement-checks-scope-not-cano
description: Input contract enforcement checks scope, not canonical paths
metadata:
  type: reference
  source: codex
  bridged: 2026-06-21
  tags: [input-validation, boundary-enforcement, unit-tests]
---

`client_private_boundary_disposition.py` accepts arbitrary queue/report paths under allowed directories but should reject non-canonical ones (accept only `data/document-index/client-private-routing-queue.jsonl`). Tests must cover path-canonicalization and rejection of lookalikes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
