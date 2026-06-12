---
name: crossprovider codex verification-queue-is-mandatory-not-optional
description: Verification queue is mandatory, not optional
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [verification-workflow, queue-management, scale-gate]
---

Append ALL provisional/raw tables to the target domain's `_verification-queue.csv`. When re-homing content, move queue rows to the target domain. This queue is load-bearing for scale ingests and gates verification completion.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
