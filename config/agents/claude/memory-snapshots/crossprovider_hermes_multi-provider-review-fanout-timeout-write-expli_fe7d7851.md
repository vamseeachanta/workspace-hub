---
name: crossprovider hermes multi-provider-review-fanout-timeout-write-expli
description: Multi-provider review fanout timeout: write explicit stub, not empty file
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [review-dispatch, adversarial-review, error-handling]
---

When Claude/Codex/Gemini fanout reviews timeout during adversarial review, write an explicit artifact with the provider name + timeout reason (e.g., `2026-05-19-plan-2754-claude.md: UNAVAILABLE — fanout timeout`). Empty files leave downstream reviewers unsure if the provider didn't run or failed silently.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
