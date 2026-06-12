---
name: crossprovider gemini work-queue-items-require-strict-frontmatter-sche
description: Work queue items require strict frontmatter schema: plan_reviewed, plan_approved, provider, complexity
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [work-queue, agents, governance]
---

Missing or mistyped frontmatter in active WRK items breaks agent routing without clear errors. Enforce via pre-commit/CI gate.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
