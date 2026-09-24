---
name: crossprovider codex adversarial-re-review-after-discriminating-tests
description: Adversarial re-review after discriminating tests surfaces implementation gaps
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [code-review, testing, quality]
---

When initial adversarial review finds MAJOR issues, add focused red tests that directly exercise the failure path, implement fixes, then run re-review. This cycle often catches gaps that simple test passes would mask—e.g., a null-handling path that correctly rejects input but uses the wrong comparison operator.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
