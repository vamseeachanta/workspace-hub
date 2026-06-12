---
name: crossprovider codex hermes-rate-limit-fallback-cascade-quota-exhaust
description: Hermes rate-limit fallback cascade: quota exhaustion affects both primary and fallback providers
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [hermes, rate-limits, provider-fallback, quota]
---

When Gemini hits free-tier quota limits (429 RESOURCE_EXHAUSTED), fallback to GitHub Copilot/Claude Sonnet also immediately hits quota (429 quota exceeded). Fallback providers don't help if the root issue is per-provider quota; requires switching to a different provider tier or account, not just retry logic.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
