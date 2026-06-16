---
name: crossprovider codex review-result-chains-and-plan-references-overwri
description: Review-result chains and plan references: overwritten findings are discard candidates
metadata:
  type: reference
  source: codex
  bridged: 2026-06-15
  tags: [review-artifacts, cleanup, plan-references]
---

When a plan references review-result directories (r3, r4, r5), check whether later audit phases overwrote substantive findings (e.g., MAJOR→UNAVAILABLE). Overwritten results are incomplete reruns or failed provider calls, not durable evidence, and should not be preserved in cleanup commits. Preserve only results that are still referenced and substantive.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
