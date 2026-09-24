---
name: crossprovider gemini review-artifacts-must-be-pushed-and-published
description: Review artifacts must be pushed and published
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [workflow-governance, gate-evidence, publication]
---

User review stages (5 draft plan, 7 final plan, 17 implementation close) now require mandatory push to origin and publish evidence logging via `log-user-review-publish.sh`, not just browser open. Review artifacts must be origin-tracked for gate audit trails.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
