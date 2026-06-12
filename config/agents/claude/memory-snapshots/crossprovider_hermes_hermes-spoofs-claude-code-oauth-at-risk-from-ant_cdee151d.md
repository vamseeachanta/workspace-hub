---
name: crossprovider hermes hermes-spoofs-claude-code-oauth-at-risk-from-ant
description: Hermes spoofs Claude Code OAuth; at risk from Anthropic policy
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes-architecture, provider-risk, auth]
---

Hermes uses anthropic-oauth-2 credential (PKCE spoof of Claude Code OAuth) to bypass auth. Anthropic Apr 4 policy warns against this pattern; account could be rate-limited or flagged. Monitor anthropic.com/billing weekly when using Hermes. Keep alternative providers (OpenRouter, Gemini API Direct) active as fallback.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
