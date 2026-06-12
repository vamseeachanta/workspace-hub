---
name: crossprovider hermes factual-assumption-verification-before-plan-revi
description: Factual assumption verification before plan review
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [planning, verification, blockers, code-truth]
---

Plans often make claims about blocker status (e.g., 'X is blocked by gate Y'). Verify against actual code—hooks, config, live behavior—before review. False narratives (claiming something is blocked when it's not) create credibility gaps that reviewers catch late, triggering full rewrites.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
