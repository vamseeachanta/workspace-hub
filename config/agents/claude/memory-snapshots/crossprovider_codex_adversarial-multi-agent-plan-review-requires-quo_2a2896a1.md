---
name: crossprovider codex adversarial-multi-agent-plan-review-requires-quo
description: Adversarial multi-agent plan review requires quorum resilience and explicit fallback
metadata:
  type: reference
  source: codex
  bridged: 2026-06-30
  tags: [adversarial-review, multi-agent-workflow, quorum, plan-review]
---

When using multiple independent reviewers (Claude, Gemini, Codex) for complex plan reviews, define explicit fallback behavior when one agent is unavailable (e.g., authentication failures). Default to requiring human decision rather than silently accepting degraded verdicts. Codex r23 and r24 reviews showed that missing quorum authority and degradation strategy blocks status transition.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
