---
name: crossprovider codex plan-approval-waiver-requirement-and-multi-provi
description: Plan approval waiver requirement and multi-provider default
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [planning, review-routing, approval-gate, policy]
---

Default plan review routing is multi-provider: Claude + Codex + Gemini per `docs/standards/AI_REVIEW_ROUTING_POLICY.md`. Single-author or deferred-review lanes require explicit user waiver before approval. Absence of required review artifacts (e.g., missing Codex or Gemini review files) is a MAJOR blocker unless user has explicitly approved deferred scope.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
