---
name: crossprovider gemini policy-only-scope-narrow-unblocks-repeated-imple
description: Policy-only scope narrow unblocks repeated implementation review cycles
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [planning-pattern, review-cycles, scope-management]
---

When a plan undergoes multiple revision rounds (v1→v6), implementation details cycling through reviews while policy content stabilizes, moving implementation pseudocode to a separate follow-on issue with TDD-first approach resolves MAJOR→MINOR verdicts. Example: #2289 v1-v3 iterated observer/approval-intent logic; v4 scope-narrowed to policy-only and filed #2445 for implementation.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
