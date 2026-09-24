---
name: crossprovider codex three-gate-safety-model-for-git-lease-dispatch
description: Three-gate safety model for git lease dispatch
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [lease, dispatch, concurrency, git, correctness-critical]
---

Lease-based dispatch requires three independent gates: (1) non-reentrant acquisition (same holder/host can both succeed), (2) atomic CAS-fenced delete with token+SHA verification to prevent cross-holder deletion, (3) pre-exec token verification immediately before eval/ssh. Weak lease naming (cksum) causes collisions across unrelated commands—use strong digests instead.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
